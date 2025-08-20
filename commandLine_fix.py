# commandLine_fix.py
# -- coding: utf-8 -*-

import argparse, os, time
from repair_core import (
    INPUT_FOLDER, OUTPUT_FOLDER,
    read_input_code, write_output_code,fix_code_with_llm
)

def parse_args():
    parser = argparse.ArgumentParser(description="自動化修補程式碼漏洞 (使用 GPT API)")
    parser.add_argument("--input", type=str,nargs="+", help="輸入的漏洞程式碼",required=True)
    parser.add_argument("--function_name", nargs="+",type=str, help="目標函數名稱例如 'vulnerable_function'")
    parser.add_argument("--output", type=str, help="修補後的程式碼輸出",default="fixed_code.")
    parser.add_argument("--model", type=str, help="使用的 GPT 模型",default="gpt-4o")
    parser.add_argument("--temperature", type=float, help="模型生成溫度，控制隨機性",default=0.2)
    parser.add_argument("--enable_error_check",action="store_true",help="啟用錯誤檢查功能")
    parser.add_argument("--error_message",type=str,default="",help="編譯後得到的錯誤訊息，只有在--enable_error_check 啟用時才會使用")
    return parser.parse_args()

def main():
    args = parse_args()
    functions = args.function_name if args.function_name else [None] * len(args.input) 
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    for idx, input_file in enumerate(args.input):
        fn = functions[idx] if idx < len(functions) else None
        output_filename = f"fixed2_{os.path.splitext(input_file)[0]}.txt"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        try:
            t0 = time.time()
            code_snippet = read_input_code(input_file)
            fixed_code = fix_code_with_llm(code_snippet=code_snippet, function_name=fn, model=args.model, temperature=args.temperature,
                                           error_message=(args.error_message if args.enable_error_check and args.error_message else None)
            )
            write_output_code(output_path, fixed_code)
            print(f"[✓] 修補後的程式碼已儲存到 {output_path}  （耗時 {time.time()-t0:.2f}s）")
            
        except Exception as e:
            print(f"[✗] 處理 {input_file} 時發生錯誤：{e}")

if __name__ == "__main__":
    main()