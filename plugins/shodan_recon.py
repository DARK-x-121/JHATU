import os
import re
import requests
from colorama import Fore

# Auto load Shodan Key from environment
SHODAN_KEY = os.getenv("SHODAN_API_KEY")

def extract_ip(text):
    """Detects standard IPv4 format in user input"""
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    match = re.search(ip_pattern, text)
    return match.group(0) if match else None

def query_shodan(ip):
    """Calls Shodan REST API directly"""
    if not SHODAN_KEY:
        return f"{Fore.RED}[!] SHODAN_API_KEY missing in .env file!{Fore.WHITE}"
        
    url = f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_KEY}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            
            org = data.get('org', 'N/A')
            isp = data.get('isp', 'N/A')
            country = data.get('country_name', 'N/A')
            ports = data.get('ports', [])
            vulns = list(data.get('vulns', {}).keys())
            
            output = f"{Fore.GREEN}[+] Ethical Shodan OSINT Report for [{ip}]:{Fore.WHITE}\n"
            output += f" • Organization : {org}\n"
            output += f" • ISP          : {isp}\n"
            output += f" • Location     : {country}\n"
            output += f" • Open Ports   : {ports}\n"
            output += f" • Known CVEs   : {vulns if vulns else 'No critical vulnerabilities listed'}\n"
            return output
        elif res.status_code == 404:
            return f"{Fore.YELLOW}[*] Shodan has no records for IP: {ip}{Fore.WHITE}"
        else:
            return f"{Fore.RED}[-] Shodan API Error ({res.status_code}): {res.text}{Fore.WHITE}"
            
    except Exception as e:
        return f"{Fore.RED}[-] Recon Request Failed: {e}{Fore.WHITE}"

def run_plugin(user_input):
    """
    Main plugin execution interface called automatically by main.py
    """
    input_lower = user_input.lower()
    
    # Intent keywords detection
    recon_keywords = ["scan", "osint", "shodan", "recon", "ip details", "check ip"]
    
    if any(keyword in input_lower for keyword in recon_keywords):
        target_ip = extract_ip(user_input)
        if target_ip:
            print(f"{Fore.CYAN}[*] Triggering Shodan Recon Module for {target_ip}...{Fore.WHITE}")
            return query_shodan(target_ip)
            
    return None

  
