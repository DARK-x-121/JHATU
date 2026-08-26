                import os
import sys
import re
import time
import importlib
import pkgutil
import requests
from datetime import datetime
from dotenv import load_dotenv
from colorama import Fore, Style, init

init(autoreset=True)
load_dotenv()

from config import BANNER
from auth import verify_access
from system_tools import create_local_file

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


AVAILABLE_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "mixtral-8x7b-32768"
]

def load_dynamic_plugins():
    """Auto-detects and loads all python scripts from 'plugins' directory"""
    loaded_plugins = []
    if os.path.exists("plugins"):
        for _, module_name, _ in pkgutil.iter_modules(["plugins"]):
            try:
                module = importlib.import_module(f"plugins.{module_name}")
                if hasattr(module, "run_plugin"):
                    loaded_plugins.append(module)
            except Exception as e:
                print(f"{Fore.RED}[-] Plugin Load Error ({module_name}): {e}")
    return loaded_plugins

def call_groq_api(api_key, messages):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    for model_name in AVAILABLE_MODELS:
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 2048
        }
        try:
            res = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content']
        except Exception:
            continue

    return f"{Fore.RED}[!] Error: Groq APIs unavailable or model names outdated."

def main():
    verify_access()
    os.system("clear" if os.name != "nt" else "cls")
    print(BANNER)
    
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print(f"{Fore.RED}[!] GROQ_API_KEY missing in .env file!")
        sys.exit(1)
        
    plugins = load_dynamic_plugins()
    
    
    print(f"{Fore.CYAN}┌──({Fore.GREEN}SYSTEM STATUS{Fore.CYAN})")
    print(f"{Fore.CYAN}├── Dynamic Modules : {Fore.YELLOW}{len(plugins)} Plugin(s) Loaded")
    print(f"{Fore.CYAN}├── Engine Core     : {Fore.YELLOW}Groq AI Multi-Fallback Engine")
    print(f"{Fore.CYAN}└── Cyber Shell     : {Fore.GREEN}Active {Fore.WHITE}(Type 'exit' to disconnect)")
    print(f"{Fore.BLUE}═" * 55 + "\n")

    messages = [
        {"role": "system", "content": "You are JHATU, an elite Cybersecurity Assistant created by Amit (Team Dark). Provide precise, technical, and ethical answers."}
    ]

    while True:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            prompt_ui = f"{Fore.RED}┌──[{Fore.WHITE}JHATU-AI{Fore.RED}]─[{Fore.CYAN}{timestamp}{Fore.RED}]\n{Fore.RED}└──{Fore.YELLOW}⚔{Fore.WHITE} "
            
            cmd = input(prompt_ui).strip()
            if not cmd:
                continue
            if cmd.lower() in ["exit", "quit", "clear"]:
                if cmd.lower() == "clear":
                    os.system("clear" if os.name != "nt" else "cls")
                    print(BANNER)
                    continue
                print(f"{Fore.YELLOW}[*] Shutting down JHATU AI Interface...")
                break

            
            plugin_handled = False
            for plugin in plugins:
                result = plugin.run_plugin(cmd)
                if result:
                    print(f"\n{result}\n")
                    plugin_handled = True
                    break

            if plugin_handled:
                print(f"{Fore.BLUE}─" * 55)
                continue

            
            print(f"{Fore.CYAN}[*] Processing response...", end="\r")
            messages.append({"role": "user", "content": cmd})
            
            output = call_groq_api(groq_key, messages)
            
            
            print(" " * 30, end="\r") # Clear processing text
            print(f"{Fore.GREEN}┌──[ {Fore.WHITE}JHATU RESPONSE{Fore.GREEN} ]")
            for line in output.split("\n"):
                print(f"{Fore.GREEN}│ {Fore.WHITE}{line}")
            print(f"{Fore.GREEN}└" + "─" * 50 + "\n")

            messages.append({"role": "assistant", "content": output})

            # Auto-save Script Feature
            code_blocks = re.findall(r'```(?:html|python|bash)?\n(.*?)```', output, re.DOTALL)
            if code_blocks and any(w in cmd.lower() for w in ["write", "create", "generate", "code"]):
                ext = "html" if "html" in cmd.lower() else "py"
                status = create_local_file(f"jhatu_script.{ext}", code_blocks[0].strip())
                print(f"{status}\n")

            print(f"{Fore.BLUE}─" * 55)

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Session Terminated.")
            break
        except Exception as e:
            print(f"{Fore.RED}[-] Execution Error: {e}\n")

if __name__ == "__main__":
    main()
                    
