import os
import re
from config import PROJECTS_DIR
from colorama import Fore


def _safe_filename(filename):
    """Strips path separators and unsafe characters so saves can't escape PROJECTS_DIR."""
    name = os.path.basename(filename)
    name = re.sub(r'[^A-Za-z0-9._-]', '_', name)
    return name or "jhatu_output.txt"


def create_local_file(filename, code_content):
    try:
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        filepath = os.path.join(PROJECTS_DIR, _safe_filename(filename))

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_content)

        return f"{Fore.GREEN}[+] File saved at: {filepath}"
    except Exception as e:
        return f"{Fore.RED}[-] File Error: {e}"
