import sys
from config import SYSTEM_PASSWORD
from colorama import Fore

def verify_access():
    print(Fore.YELLOW + "[*] Authentication Required")
    pwd = input(Fore.WHITE + "Enter Password: ").strip()
    
    if pwd == SYSTEM_PASSWORD:
        print(Fore.GREEN + "[+] Access Granted!\n")
        return True
    else:
        print(Fore.RED + "[-] Incorrect Password. Access Denied.")
        sys.exit(1)
      
