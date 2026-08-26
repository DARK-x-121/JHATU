import os
from config import PROJECTS_DIR
from colorama import Fore

def create_local_file(filename, code_content):
    try:
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        filepath = os.path.join(PROJECTS_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_content)
            
        return f"{Fore.GREEN}[+] File saved at: {filepath}"
    except Exception as e:
        return f"{Fore.RED}[-] File Error: {e}"
      
