
# -*- coding: utf-8 -*-
import argparse
import os
import openai
import re
import time
import logging  # type: ignore
from datetime import datetime  # type: ignore       
from dotenv import load_dotenv  # type: ignore
load_dotenv()

client = openai.ChatCompletion
model = "gpt-4o"
INPUT_FOLDER = "fixed_input"
OUTPUT_FOLDER = "fixed_output"
#client = OpenAI()
# completion = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[
#         {
#             "role": "system",
#             "content": "Talk like a expert. and say this is a bigmac."
#         },
#         {
#             "role": "user",
#             "content": "Say this is a test."
#       
#   }
#     ],
#     n=2
# )

# print(completion.choices[0].message.content.strip()+"\n"+completion.choices[1].message.content.strip())

def parse_args():
    parser = argparse.ArgumentParser(description="自動化修補程式碼漏洞 (使用 GPT API)")
    parser.add_argument("--input", type=str, help="輸入的錯誤程式碼",required=True)
    parser.add_argument("--function_name", type=str, help="目標函數名稱例如 'vulnerable_function'")
    parser.add_argument("--output", type=str, help="修補後的程式碼輸出",default="fixed_code.")
    parser.add_argument("--model", type=str, help="使用的 GPT 模型",default="gpt-4o")
    parser.add_argument("--temperature", type=float, help="模型生成溫度，控制隨機性",default=0.2)
    return  parser.parse_args()


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
        

# def construct_prompt(code_snippet, function_name=None):
#     prompt = "You are a security expert skilled in analyzing source code for vulnerabilities. Your task is to follow a four-step process to identify whether a vulnerability exists in the provided code:"
#     if function_name:
#         prompt += f"\nPlease pay special attention to fixing issues in the function '{function_name}'."
#     prompt += "\n\n### Original Code:\n"
#     prompt += "```c\n" + code_snippet + "\n```\n"
#     prompt += "\nPlease provide the corrected, complete, and compilable C code, and reply in a markdown code block format."
#     return prompt


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
        "- All necessary imports and headers required for this function to compile or run correctly.\n"
        "- Use English `//` or `#` comments to explain the applied security fixes.\n"
        "- Do **not** change the original function name.\n"
        "- Do **not** provide explanations outside the code block.\n"
    )
    return prompt


def call_gpt_api(prompt, model="gpt-4", temperature=0.2):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    return response

def extract_code_from_response(response):
    message = response.choices[0].message["content"]
    code_blocks = re.findall(r"```c\s*(.*?)\s*```", message, re.DOTALL)
    if code_blocks:
        return code_blocks[0]
    else:
        return message

def write_output_code(output_file, code):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(code)




def main():
    args = parse_args()
    openai.api_key = get_api_key()

    

    code_snippet = read_input_code(args.input)
    prompt = construct_prompt(code_snippet, args.function_name)

    # print("修補前的程式碼：")
    # print(code_snippet)
    # print("\n\n")

    print("=== 發送的 Prompt ===")
    print(prompt)
    print("=======================")

    
    try:
        response = call_gpt_api(prompt, model=args.model, temperature=args.temperature)
    except Exception as e:
        print("呼叫 GPT API 時發生錯誤：", e)
        return

    fixed_code = extract_code_from_response(response)
    
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    output_file_path = os.path.join(OUTPUT_FOLDER, args.output)
    write_output_code(output_file_path, fixed_code)
    print(f"修補後的程式碼已儲存到 {output_file_path}")

    # write_output_code(args.output, fixed_code)
    # print(f"修補後的程式碼已儲存到 {args.output}")
    return

if __name__ == "__main__":
    main()
