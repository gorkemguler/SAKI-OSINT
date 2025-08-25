import argparse
import asyncio
from colorama import Fore, Style, init
import sys

# Import modules
from modules.email_breach import check_email_breach
from modules.username import search_usernames
from modules.email_recon import search_email_registrations
from modules.phone import check_phone_number
from modules.domain import analyze_domain

def _print_and_save_output(content_lines, output_file_path=None):
    """Prints content to console and optionally saves to a file, stripping color codes."""
    for line in content_lines:
        print(line)
    
    if output_file_path:
        with open(output_file_path, 'a') as f:
            # Strip color codes before writing to file
            clean_lines = [line.replace(Fore.GREEN, '').replace(Fore.RED, '').replace(Fore.YELLOW, '').replace(Fore.CYAN, '').replace(Fore.WHITE, '').replace(Style.RESET_ALL, '') for line in content_lines]
            f.write("\n".join(clean_lines) + "\n")

def display_banner():
    banner = f"""
{Fore.CYAN}.oooooo..o       .o.       oooo    oooo ooooo      
d8P'    `Y8      .888.      `888   .8P'  `888'      
Y88bo.          .8"888.      888  d8'     888       
 `"Y8888o.     .8' `888.     88888[       888       
     `"Y88b   .88ooo8888.    888`88b.     888       
oo     .d8P  .8'     `888.   888  `88b.   888       
8""88888P'  o88o     o8888o o888o  o888o o888o      
{Fore.WHITE}                            █▀█ █▀ █ █▄░█ ▀█▀
                            █▄█ ▄█ █ █░▀█ ░█░{Style.RESET_ALL}

{Fore.WHITE}A Comprehensive Open Source Intelligence Tool{Style.RESET_ALL}
"""
    print(banner)

def main():
    init(autoreset=True)

    parser = argparse.ArgumentParser(description="SAKI OSINT - A comprehensive OSINT tool.")
    parser.add_argument('-o', '--output', type=str, help='Output file to save results.')
    args = parser.parse_args()

    display_banner()

    while True:
        output_content = []
        output_content.append(f"{Fore.MAGENTA}\nChoose a module to run:{Style.RESET_ALL}")
        output_content.append(f"  {Fore.BLUE}1. Email Breach Check{Style.RESET_ALL}")
        output_content.append(f"  {Fore.BLUE}2. Username Search{Style.RESET_ALL}")
        output_content.append(f"  {Fore.BLUE}3. Email Registration Recon{Style.RESET_ALL}")
        output_content.append(f"  {Fore.BLUE}4. Phone Number Analysis{Style.RESET_ALL}")
        output_content.append(f"  {Fore.BLUE}5. Domain Analysis{Style.RESET_ALL}")
        output_content.append(f"  {Fore.RED}6. Exit{Style.RESET_ALL}")
        _print_and_save_output(output_content)

        choice = input(f"{Fore.GREEN}Enter your choice (1-6): {Style.RESET_ALL}").strip()

        if choice == '1':
            email = input(f"{Fore.YELLOW}Enter email address for breach check: {Style.RESET_ALL}").strip()
            output_content = []
            output_content.append(f"[*] Checking for breaches for {Fore.CYAN}{email}{Style.RESET_ALL}...")
            result = check_email_breach(email)

            if result and "breaches" in result:
                breaches = result["breaches"]
                if breaches:
                    output_content.append(f"{Fore.GREEN}[+] Found {len(breaches)} breaches:{Style.RESET_ALL}")
                    for breach in breaches:
                        output_content.append(f"  {Fore.YELLOW}----------------------------------------{Style.RESET_ALL}")
                        output_content.append(f"  {Fore.RED}Name         : {breach.get('Name')}{Style.RESET_ALL}")
                        output_content.append(f"  {Fore.WHITE}Domain       : {breach.get('Domain')}")
                        output_content.append(f"  {Fore.WHITE}Breach Date  : {breach.get('BreachDate')}")
                        dataclasses = ", ".join(breach.get('DataClasses', []))
                        output_content.append(f"  {Fore.WHITE}Data Classes : {dataclasses}")
                else:
                     output_content.append(f"{Fore.GREEN}[-] No breaches found for {email}.{Style.RESET_ALL}")
            elif result and "error" in result:
                output_content.append(f"{Fore.RED}[!] An error occurred: {result['error']}{Style.RESET_ALL}")
            else:
                output_content.append(f"{Fore.GREEN}[-] No breaches found for {email}.{Style.RESET_ALL}")
            
            _print_and_save_output(output_content, args.output)

        elif choice == '2':
            username = input(f"{Fore.YELLOW}Enter username to search: {Style.RESET_ALL}").strip()
            output_content = []
            output_content.append(f"[*] Searching for username: {Fore.CYAN}{username}{Style.RESET_ALL}...")
            results = asyncio.run(search_usernames(username))
            
            found_count = 0
            for site, url, status in results:
                if status is True:
                    output_content.append(f"{Fore.GREEN}[+] {site}: {url}")
                    found_count += 1
            if found_count == 0:
                output_content.append(f"{Fore.RED}[-] No accounts found for {username}.{Style.RESET_ALL}")
            
            _print_and_save_output(output_content, args.output)

        elif choice == '3':
            email = input(f"{Fore.YELLOW}Enter email address for registration recon: {Style.RESET_ALL}").strip()
            output_content = []
            output_content.append(f"[*] Checking email registrations for {Fore.CYAN}{email}{Style.RESET_ALL}...")
            results = asyncio.run(search_email_registrations(email))
            
            found_count = 0
            for site, url, status in results:
                if status is True:
                    output_content.append(f"{Fore.GREEN}[+] {site}: Registered")
                    found_count += 1
                elif status is False:
                    output_content.append(f"{Fore.RED}[-] {site}: Not Registered")
                else:
                    output_content.append(f"{Fore.YELLOW}[?] {site}: {status}")
            if found_count == 0:
                output_content.append(f"{Fore.RED}[-] No registrations found for {email}.{Style.RESET_ALL}")
            
            _print_and_save_output(output_content, args.output)

        elif choice == '4':
            phone_number = input(f"{Fore.YELLOW}Enter phone number (e.g., +15551234567): {Style.RESET_ALL}").strip()
            output_content = []
            output_content.append(f"[*] Analyzing phone number: {Fore.CYAN}{phone_number}{Style.RESET_ALL}...")
            results = check_phone_number(phone_number)

            if results["valid"]:
                output_content.append(f"{Fore.GREEN}[+] Phone number is valid.{Style.RESET_ALL}")
                output_content.append(f"  {Fore.WHITE}Country Code   : {results['country_code']}")
                output_content.append(f"  {Fore.WHITE}National Number: {results['national_number']}")
                if results["carrier"]:
                    output_content.append(f"  {Fore.WHITE}Carrier        : {results['carrier']}")
                if results["location"]:
                    output_content.append(f"  {Fore.WHITE}Location       : {results['location']}")
                
                if results["online_mentions"]:
                    output_content.append(f"{Fore.GREEN}[+] Found online mentions:{Style.RESET_ALL}")
                    for mention in results["online_mentions"]:
                        output_content.append(f"  {Fore.CYAN}- {mention}{Style.RESET_ALL}")
                else:
                    output_content.append(f"{Fore.YELLOW}[-] No online mentions found.{Style.RESET_ALL}")
            else:
                output_content.append(f"{Fore.RED}[-] Phone number is invalid or an error occurred: {results.get('error', 'Unknown error')}{Style.RESET_ALL}")
            
            _print_and_save_output(output_content, args.output)

        elif choice == '5':
            domain = input(f"{Fore.YELLOW}Enter domain name (e.g., example.com): {Style.RESET_ALL}").strip()
            output_content = []
            output_content.append(f"[*] Analyzing domain: {Fore.CYAN}{domain}{Style.RESET_ALL}...")
            results = analyze_domain(domain)

            output_content.append(f"{Fore.GREEN}[+] WHOIS Information:{Style.RESET_ALL}")
            output_content.append(results["whois"])
            
            output_content.append(f"{Fore.GREEN}[+] DNS Information:{Style.RESET_ALL}")
            for record_type, records in results["dns"].items():
                if records:
                    output_content.append(f"  {Fore.WHITE}{record_type} Records:{Style.RESET_ALL}")
                    for record in records:
                        output_content.append(f"    {Fore.CYAN}- {record}{Style.RESET_ALL}")
                else:
                    output_content.append(f"  {Fore.YELLOW}{record_type} Records: Not Found{Style.RESET_ALL}")
            
            output_content.append(f"{Fore.GREEN}[+] Common Subdomains:{Style.RESET_ALL}")
            if results["subdomains"]:
                for subdomain in results["subdomains"]:
                    output_content.append(f"  {Fore.CYAN}- {subdomain}{Style.RESET_ALL}")
            else:
                output_content.append(f"{Fore.YELLOW}[-] No common subdomains found.{Style.RESET_ALL}")

            output_content.append(f"{Fore.GREEN}[+] SSL/TLS Versions:{Style.RESET_ALL}")
            if results["ssl_tls_versions"]:
                for version in results["ssl_tls_versions"]:
                    output_content.append(f"  {Fore.CYAN}- {version}{Style.RESET_ALL}")
            else:
                output_content.append(f"{Fore.YELLOW}[-] No SSL/TLS versions found or could not be checked.{Style.RESET_ALL}")

            if results["private_ip_warning"]:
                output_content.append(f"{Fore.RED}[!] WARNING: Private IP address(es) found in DNS records!{Style.RESET_ALL}")

            output_content.append(f"{Fore.GREEN}[+] Email Authentication Records (SPF, DMARC, DKIM):{Style.RESET_ALL}")
            if results["dns"].get('SPF'):
                output_content.append(f"  {Fore.WHITE}SPF Records:{Style.RESET_ALL}")
                for record in results["dns"]['SPF']:
                    output_content.append(f"    {Fore.CYAN}- {record}{Style.RESET_ALL}")
            else:
                output_content.append(f"{Fore.YELLOW}SPF Records: Not Found{Style.RESET_ALL}")

            if results["dns"].get('DMARC'):
                output_content.append(f"  {Fore.WHITE}DMARC Records:{Style.RESET_ALL}")
                for record in results["dns"]['DMARC']:
                    output_content.append(f"    {Fore.CYAN}- {record}{Style.RESET_ALL}")
            else:
                output_content.append(f"{Fore.YELLOW}DMARC Records: Not Found{Style.RESET_ALL}")

            if results["dns"].get('DKIM'):
                output_content.append(f"  {Fore.WHITE}DKIM Records:{Style.RESET_ALL}")
                for record in results["dns"]['DKIM']:
                    output_content.append(f"    {Fore.CYAN}- {record}{Style.RESET_ALL}")
            else:
                output_content.append(f"{Fore.YELLOW}DKIM Records: Not Found{Style.RESET_ALL}")
            
            _print_and_save_output(output_content, args.output)

        elif choice == '6':
            output_content.append(f"{Fore.GREEN}Exiting SAKI OSINT. Goodbye!{Style.RESET_ALL}")
            _print_and_save_output(output_content, args.output)
            sys.exit()

        else:
            output_content.append(f"{Fore.RED}Invalid choice. Please enter a number between 1 and 6.{Style.RESET_ALL}")
            _print_and_save_output(output_content, args.output)

if __name__ == "__main__":
    main()
