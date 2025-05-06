
# -*- coding: utf-8 -*-
import argparse
import os
import openai
import re
import time
import logging  # type: ignore
from datetime import datetime  # type: ignore       
from dotenv import load_dotenv  # type: ignore

load_dotenv('.env', override=True)


client = openai.ChatCompletion
model = "gpt-4o"
INPUT_FOLDER = "fixed_input"
OUTPUT_FOLDER = "fixed_output"

def parse_args():
    parser = argparse.ArgumentParser(description="自動化修補程式碼漏洞 (使用 GPT API)")
    parser.add_argument("--input", type=str,nargs="+", help="輸入的錯誤程式碼",required=True)
    parser.add_argument("--function_name", nargs="+",type=str, help="目標函數名稱例如 'vulnerable_function'")
    parser.add_argument("--output", type=str, help="修補後的程式碼輸出",default="fixed_code.")
    parser.add_argument("--model", type=str, help="使用的 GPT 模型",default="gpt-4o")
    parser.add_argument("--temperature", type=float, help="模型生成溫度，控制隨機性",default=0.2)
    parser.add_argument("--enable_error_check",action="store_true",help="啟用錯誤檢查功能")
    parser.add_argument("--error_message",type=str,default="",help="編譯後得到的錯誤訊息，只有在--enable_error_check 啟用時才會使用")
    return parser.parse_args()


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

    inputs = args.input
    functions = args.function_name if args.function_name else [None] * len(inputs)

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)


    for idx, input_file in enumerate(inputs):
        function_name = functions[idx] if idx < len(functions) else None
        output_filename = f"fixed_{os.path.splitext(input_file)[0]}.txt"

        try:
            code_snippet = read_input_code(input_file)
            prompt = construct_prompt(code_snippet, function_name)
            print(f"\n=== [Prompt for {input_file}] ===")
            print(prompt)
            print("==================================")

            response = call_gpt_api(prompt, model=args.model, temperature=args.temperature)
            fixed_code = extract_code_from_response(response)

            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            write_output_code(output_path, fixed_code)
            print(f"[✓] 修補後的程式碼已儲存到 {output_path}")

            # -- 如果啟用回饋機制且有外部錯誤，就把錯誤訊息拼到 prompt，再次修正並覆蓋 --
            if args.enable_error_check and args.error_message:
                print ("→ 收到外部編譯錯誤，回饋 GPT 進行二次修正…")
                fix_prompt = prompt + "\n\n/* 外部編譯錯誤回饋 */\n" + args.error_message + "\n請依此修正程式碼 */" 
                response2 = call_gpt_api(fix_prompt, model=args.model, temperature=args.temperature)
                fixed_code2 = extract_code_from_response(response2)
                write_output_code(output_path, fixed_code2)
                print(f"[✓] 已覆蓋 {output_filename}，並生成修正後版本。")
            
                
        except Exception as e:
            print(f"[✗] 錯誤發生於 {input_file}：{e}")


if __name__ == "__main__":
    main()
