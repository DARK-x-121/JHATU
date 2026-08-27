import sys
from getpass import getpass
from config import SYSTEM_PASSWORD
from colorama import Fore

MAX_ATTEMPTS = 3


def verify_access():
    """Prompts for the system password, allowing a few retries before exiting."""
    print(Fore.YELLOW + "[*] Authentication Required")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            pwd = getpass(Fore.WHITE + "Enter Password: ").strip()
        except (KeyboardInterrupt, EOFError):
            print(Fore.YELLOW + "\n[*] Authentication cancelled.")
            sys.exit(1)

        if pwd == SYSTEM_PASSWORD:
            print(Fore.GREEN + "[+] Access Granted!\n")
            return True

        remaining = MAX_ATTEMPTS - attempt
        if remaining > 0:
            print(Fore.RED + f"[-] Incorrect Password. {remaining} attempt(s) remaining.")
        else:
            print(Fore.RED + "[-] Incorrect Password. Access Denied.")
            sys.exit(1)
