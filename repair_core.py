# repaire_core.py
# -- coding: utf-8 -*-

from ast import arg
import os, re, time 
from dotenv import load_dotenv
import time
import openai

load_dotenv('.env', override=True)
model = "gpt-4o"
INPUT_FOLDER = "fixed_input"
OUTPUT_FOLDER = "fixed_output"

def get_api_key():

    get_key = os.getenv("OPENAI_API_KEY")
    if not get_key:
        raise ValueError("Please set your OPENAI_API_KEY in your environment variables.")
    return get_key


def read_input_code(file_path):
    readFile_path = os.path.join(INPUT_FOLDER, file_path)
    try:
        with open(readFile_path, "r", encoding="utf-8") as file:
            code = file.read()
            return code  
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {readFile_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading file: {e}")


def write_output_code(output_file, code):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(code)


def construct_prompt(code_snippet, function_name=None):
    prompt = (
        "You are a security expert skilled in analyzing source code for vulnerabilities.\n"
        "Your task is to follow a structured four-step process to determine whether the provided code contains any security vulnerabilities:\n"
        "1. Understand the overall language, structure and purpose of the code.\n"
        "2. Identify potentially vulnerable subcomponents. If no specific function is indicated, locate the sections most likely to introduce security issues.\n"
        "3. Perform a detailed analysis of these subcomponents.\n"
        "4. Conclude whether a vulnerability exists, and if so, explain the root cause briefly.\n"
    )

    if function_name:
        prompt += f"\nPlease pay special attention to fixing issues in the function `{function_name}`.\n"

    prompt += (
        "\n### Original Code:\n" + code_snippet + "\n\n"
        "\nPlease provide the corrected, complete, and runnable code in a markdown code block.\n"
        "The output must include:\n"
        "- Only the function(s) that have been modified (leave out unrelated functions).\n"
        "- All necessary imports or headers required for this function to compile or run very correctly.\n"
        "- Use English `//` or `#` comments to explain the applied security fixes.\n"
        "- Do **not** change the original function name.\n"
        "- Do **not** provide explanations outside the code block.\n"
        "- Search for github commits, patched versions, CVE cases, etc.\n"

    )
    return prompt


def extract_code_from_response(response):
    message = response.choices[0].message.content
    code_blocks = re.findall(r"```c\s*(.*?)\s*```", message, re.DOTALL)
    if code_blocks:
        return code_blocks[0]
    else:
        return message
    

def call_gpt_api(prompt, model="gpt-4", temperature=0.2):
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    return response

def fix_code_with_llm(
    code_snippet:str,
    function_name:str | None = None,
    model:str = "gpt-4o",
    temperature: float = 0.2,
    error_message: str | None = None
) -> str:

    prompt = construct_prompt(code_snippet, function_name)
    resp = call_gpt_api(prompt, model=model, temperature=temperature)
    fixed_code = extract_code_from_response(resp)

    if error_message:
        fix_prompt = prompt + "\n\n/* 外部編譯錯誤回饋 */\n" + error_message + "\n請依此修正程式碼 */" 
        resp2 = call_gpt_api(fix_prompt, model= model, temperature=temperature)
        fixed_code = extract_code_from_response(resp2)
    return fixed_code

    # if error_message:
    #    fix_prompt = (
    #         prompt
    #         + "\n\n/* External compile/test error feedback */\n"
    #         + error_message
    #         + "\n/* Please fix accordingly. */"
    #     )
    #     resp2 = call_gpt_api(fix_prompt, model=model, temperature=temperature)
    #     fixed = extract_code_from_response(resp2)
