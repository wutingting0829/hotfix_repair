# hotfix_repair

## Set Enviroment
set the virtual machine: 
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirement.txt

## Test Results
python3 main.py --input vulnerable_example.txt
python main.py --input vulnerable_example.txt --function vulnerable_function --output fixed_code.txt
python main.py --input ngx_http_parse.c --function ngx_http_parse_chunked --output ngx_http_parse_fixed.txt


## Important
I set open_api_key to .env, but I removed it for security reasons, so remember to set your own key!
