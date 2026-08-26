import os
import sys
import re
from dotenv import load_dotenv
from colorama import Fore, Style
from groq import Groq

load_dotenv()

from config import BANNER
from auth import verify_access
from system_tools import create_local_file

def main():
    verify_access()
    print(BANNER)
    
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print(Fore.RED + "[!] GROQ_API_KEY missing in .env file!")
        sys.exit(1)
        
    client = Groq(api_key=groq_key)
    print(Fore.GREEN + "[+] JHATU AI is active. Type 'exit' to quit.\n")
    
    while True:
        try:
            cmd = input(Fore.MAGENTA + "JHATU > " + Fore.WHITE).strip()
            if not cmd:
                continue
            if cmd.lower() in ["exit", "quit"]:
                print(Fore.YELLOW + "[*] Exiting...")
                break
                
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are JHATU, an elite Cybersecurity AI built by Amit (Team Dark)."},
                    {"role": "user", "content": cmd}
                ]
            )
            
            output = response.choices[0].message.content
            print(f"\n{Fore.CYAN}JHATU:\n{Fore.WHITE}{output}\n")
            
            
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
  
