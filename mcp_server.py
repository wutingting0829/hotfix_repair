# mcp_server.py
# -*- coding: utf-8 -*-

from pathlib import Path
from mcp.server.fastmcp import FastMCP
from repair_core import (
    INPUT_FOLDER, OUTPUT_FOLDER,
    fix_code_with_llm
)

#Create an MCP server
mcp = FastMCP("Hotfix_LLM")

# Add an addition tool
@mcp.tool()
def patch_code(code: str, function_name: str | None=None, model: str = "gpt-4o", temperature: float = 0.2) -> dict:
    """
    以結構化輸入修補程式碼；回傳修補後程式碼字串。
    """
    fixed = fix_code_with_llm(code_snippet=code, function_name=function_name, model=model, temperature=temperature)
    return {"status": "ok", "patched_code": fixed}

@mcp.tool()
def patch_code_with_error(code: str, error_message: str, function_name: str | None=None, model: str = "gpt-4o", temperature: float = 0.2) -> dict:
    """
    帶入外部編譯錯誤（或測試失敗 log）進行二次修補。
    """

    fixed = fix_code_with_llm(
        code_snippet=code,
        function_name=function_name,
        model=model,
        temperature=temperature,
        error_message=error_message
    )
    return {"status": "ok", "patched_code": fixed}
 
# Add a dynamic greeting resource
ROOT = Path(".").resolve()
SAFE_DIRS = [ROOT, INPUT_FOLDER, OUTPUT_FOLDER]

@mcp.resource("workspace://list}")
def list_workspace() -> str:
    files = []
    for d in SAFE_DIRS:
        if d.exists():
            for p in d.rglob("*"):
                if p.is_file():
                    files.append(str(p.relative_to(ROOT)))
    return "\n".join(files)

@mcp.resource("workspace://file/{relpath}")
# 在「安全資料夾」範圍內讀取某個檔案的內容
def read_workspace_file(relpath: str) -> str:
    p = (ROOT / relpath).resolve()

    if not any(str(p).startswitch(str(sd)) for sd in SAFE_DIRS):
        return "[error] access denied"
    return p.read_text(errors="ignore") if p.exists() and p.is_file() else "[error] not found"

#Add a prompt
@mcp.prompt()
def secure_fix_style() -> str:
    return {
        "You are a secure code repair assistant. "
        "Follow SEI CERT rules, avoid undefined behavior, preserve semantics, add bounds checks, "
        "limit side-effects and logging."
    }

if __name__ == "__main__":
    mcp.run()