import os
from colorama import Fore, Style, init

init(autoreset=True)

# Password is read from the environment (.env) instead of being hardcoded,
# so the real credential never lives in source control.
SYSTEM_PASSWORD = os.getenv("SYSTEM_PASSWORD", "DARKJHATU2026")
PROJECTS_DIR = os.path.expanduser("~/JHATU_Projects")

BANNER = f"""
{Fore.RED}{Style.BRIGHT}
   ███████ ██   ██  █████  ████████ ██   ██ 
      ███  ██   ██ ██   ██    ██    ██   ██ 
    ███    ███████ ███████    ██    ██   ██ 
  ███      ██   ██ ██   ██    ██    ██   ██ 
 ███████   ██   ██ ██   ██    ██     ██████ 
{Fore.CYAN}  -------------------------------------------
  Author: Amit | Founder of Team Dark
  Instagram: @a.mi.t__
  Status: Operational | Cybersecurity Assistant
  -------------------------------------------
"""
