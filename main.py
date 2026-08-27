import os
import sys
import re
import importlib
import pkgutil
import requests
from datetime import datetime
from dotenv import load_dotenv
from colorama import Fore, Style, init

init(autoreset=True)

# Absolute path resolving so this works no matter where it's launched from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from config import BANNER
from auth import verify_access
from system_tools import create_local_file

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Dynamic model routing: tried in order, falls through on failure/rate-limit
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]

MAX_HISTORY_MESSAGES = 20  # keep the last N turns so the request never balloons
DIVIDER = f"{Fore.LIGHTBLACK_EX}" + ("─" * 55)


def load_dynamic_plugins():
    """Auto-detects and loads every python module in plugins/ that exposes run_plugin()."""
    loaded_plugins = []
    plugins_dir = os.path.join(BASE_DIR, "plugins")
    if os.path.exists(plugins_dir):
        if plugins_dir not in sys.path:
            sys.path.insert(0, plugins_dir)
        for _, module_name, _ in pkgutil.iter_modules([plugins_dir]):
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "run_plugin"):
                    loaded_plugins.append((module_name, module))
            except Exception as e:
                print(f"{Fore.RED}[-] Plugin Load Error ({module_name}): {e}")
    return loaded_plugins


def call_groq_api(api_key, messages):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    last_error = None
    for model_name in AVAILABLE_MODELS:
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 2048,
        }
        try:
            res = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            last_error = f"HTTP {res.status_code}: {res.text[:200]}"
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            continue

    return f"{Fore.RED}[!] All models unavailable. Last error: {last_error}"


def trim_history(messages):
    """Keeps the system prompt plus the most recent MAX_HISTORY_MESSAGES turns."""
    if len(messages) <= MAX_HISTORY_MESSAGES + 1:
        return messages
    return [messages[0]] + messages[-MAX_HISTORY_MESSAGES:]


def print_header(plugin_count):
    print(DIVIDER)
    print(f"{Fore.GREEN}● {Fore.WHITE}ENGINE STATUS : {Fore.GREEN}ONLINE {Fore.LIGHTBLACK_EX}| {Fore.CYAN}MODULES: {plugin_count} LOADED")
    print(DIVIDER + "\n")


def print_help(plugins):
    print(f"\n{Fore.CYAN}Available commands:")
    print(f"{Fore.WHITE}  help          Show this message")
    print(f"{Fore.WHITE}  clear         Clear the screen and reset the banner")
    print(f"{Fore.WHITE}  exit / quit   Leave JHATU")
    if plugins:
        print(f"\n{Fore.CYAN}Loaded plugins:")
        for name, _ in plugins:
            print(f"{Fore.WHITE}  - {name}")
    print(f"\n{Fore.LIGHTBLACK_EX}Anything else is sent to the AI model directly.\n")


def main():
    verify_access()
    os.system("clear" if os.name != "nt" else "cls")
    print(Fore.RED + BANNER)

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print(f"{Fore.RED}[!] CRITICAL: GROQ_API_KEY missing in .env file at {BASE_DIR}")
        sys.exit(1)

    plugins = load_dynamic_plugins()
    print_header(len(plugins))

    messages = [
        {
            "role": "system",
            "content": (
                "You are JHATU, an elite Cybersecurity OSINT & Automation Assistant "
                "created by Amit (Team Dark). Respond with precision and clean markdown formatting."
            ),
        }
    ]

    while True:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            prompt_ui = (
                f"{Fore.RED}┌──[{Fore.WHITE}JHATU-AI{Fore.RED}]─[{Fore.LIGHTBLACK_EX}{timestamp}{Fore.RED}]\n"
                f"{Fore.RED}└──{Fore.CYAN}# {Fore.WHITE}"
            )

            cmd = input(prompt_ui).strip()
            if not cmd:
                continue

            lowered = cmd.lower()
            if lowered in ("exit", "quit"):
                print(f"{Fore.YELLOW}[*] Session closed.")
                break
            if lowered == "clear":
                os.system("clear" if os.name != "nt" else "cls")
                print(Fore.RED + BANNER)
                print_header(len(plugins))
                continue
            if lowered == "help":
                print_help(plugins)
                continue

            # 1. Plugin execution layer — first plugin that returns a result wins
            plugin_handled = False
            for _, plugin in plugins:
                result = plugin.run_plugin(cmd)
                if result:
                    print(f"\n{result}\n")
                    plugin_handled = True
                    break

            if plugin_handled:
                print(DIVIDER)
                continue

            # 2. AI model execution layer
            print(f"{Fore.YELLOW}[*] Neural Processing...", end="\r")
            messages.append({"role": "user", "content": cmd})
            messages = trim_history(messages)

            output = call_groq_api(groq_key, messages)

            print(" " * 30, end="\r")
            print(f"\n{Fore.GREEN}╔═ [ JHATU RESPONSE ]")
            for line in output.split("\n"):
                print(f"{Fore.GREEN}║ {Fore.WHITE}{line}")
            print(f"{Fore.GREEN}╚" + "═" * 50 + "\n")

            messages.append({"role": "assistant", "content": output})

            # Auto-save: if the reply has code and the user asked to write/create/generate it
            code_blocks = re.findall(r"```(?:html|python|py|bash|sh|js|javascript)?\n(.*?)```", output, re.DOTALL)
            if code_blocks and any(w in lowered for w in ["write", "create", "generate", "code", "script"]):
                if "html" in lowered:
                    ext = "html"
                elif any(w in lowered for w in ["bash", "shell", "sh script"]):
                    ext = "sh"
                elif any(w in lowered for w in ["js", "javascript"]):
                    ext = "js"
                else:
                    ext = "py"
                status = create_local_file(f"jhatu_script.{ext}", code_blocks[0].strip())
                print(f"{Fore.YELLOW}[+] {status}\n")

            print(DIVIDER)

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Terminal session aborted.")
            break
        except Exception as e:
            print(f"{Fore.RED}[-] Core Failure: {e}\n")


if __name__ == "__main__":
    main()
