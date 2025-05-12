# hotfix_repair
## Set Enviroment
```
set the virtual machine: 
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirement.txt
```

## Test Result
```
python3 main.py --input vulnerable_example.txt
python main.py --input vulnerable_example.txt --function vulnerable_function --output fixed_code.txt
python main.py --input ngx_http_parse.c --function ngx_http_parse_chunked --output ngx_http_parse_fixed.txt
```

## Update
### Add new function: Error Feedback Controller, optional (in the branch)
* Function: When the user receives an error message during the external compilation phase, the error content is fed back to LLM to generate a second revision.
* Implementation: Use the --enable_error_check flag and the --error_message parameter to determine whether to start the second stage of repair. If yes, concatenate the initial prompt and the error message and call call_gpt_api() again, overwriting the original repair file.

```
 def parse_args():
     parser = argparse.ArgumentParser(description="自動化修補程式碼漏洞 (使用 GPT API)")
     # ... 其它參數 ...
-    parser.add_argument(
-        "--enable_error_check", type=bool,
-        help="啟用錯誤回饋機制（只有有錯誤訊息時才回饋 GPT）"
-    )
+    parser.add_argument(
+        "--enable_error_check",
+        action="store_true",
+        help="啟用錯誤回饋機制（只有帶 --error_message 時才啟動二次修正）"
+    )
     parser.add_argument(
         "--error_message", type=str, default="",
         help="外部編譯後得到的錯誤訊息，只有在 --enable_error_check 時使用"
     )

```

### How to Test
* Execute in the project root directory: With switch, without error message → Only enable flag, but because there is no error_message, no secondary correction will be performed
```
python3 repaire_main.py \
  --input test.txt \
  --function_name vulnerable_function \
  --enable_error_check
```
you may see this : `[✓] 初次修正程式碼已儲存到 fixed_output/fixed_test.txt`

* With error message: At this time, args.enable_error_check will be True, and args.error_message is not empty, which will trigger the "second feedback to GPT and overwrite" process.   
```
python3 repaire_main.py \
  --input test.txt \
  --function_name vulnerable_function \
  --enable_error_check \
  --error_message "test.txt:4:5: error: expected ‘;’ before ‘printf’"

```
