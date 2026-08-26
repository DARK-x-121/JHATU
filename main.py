import os
import sys
import re
import requests
from dotenv import load_dotenv
from colorama import Fore, Style

load_dotenv()

from config import BANNER
from auth import verify_access
from system_tools import create_local_file

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def call_groq_api(api_key, messages):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 2048
    }
    
    res = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
    if res.status_code == 200:
        return res.json()['choices'][0]['message']['content']
    else:
        return f"{Fore.RED}[-] API Error ({res.status_code}): {res.text}"

def main():
    verify_access()
    print(BANNER)
    
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print(Fore.RED + "[!] GROQ_API_KEY missing in .env file!")
        sys.exit(1)
        
    messages = [
        {"role": "system", "content": "You are JHATU, an elite Cybersecurity AI built by Amit (Team Dark)."}
    ]
    
    print(Fore.GREEN + "[+] JHATU AI is active. Type 'exit' to quit.\n")
    
    while True:
        try:
            cmd = input(Fore.MAGENTA + "JHATU > " + Fore.WHITE).strip()
            if not cmd:
                continue
            if cmd.lower() in ["exit", "quit"]:
                print(Fore.YELLOW + "[*] Exiting...")
                break
                
            messages.append({"role": "user", "content": cmd})
            
            output = call_groq_api(groq_key, messages)
            print(f"\n{Fore.CYAN}JHATU:\n{Fore.WHITE}{output}\n")
            
            messages.append({"role": "assistant", "content": output})
            
            # Code auto-saver logic
            code_blocks = re.findall(r'```(?:html|python|bash)?\n(.*?)```', output, re.DOTALL)
            if code_blocks and ("write" in cmd.lower() or "create" in cmd.lower() or "build" in cmd.lower()):
                ext = "html" if "html" in cmd.lower() else "py"
                create_local_file(f"jhatu_script.{ext}", code_blocks[0].strip())

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}\n")

if __name__ == "__main__":
    main()
