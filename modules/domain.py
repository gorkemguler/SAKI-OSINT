import whois
import dns.resolver
import socket
import ssl
import ipaddress
import configparser
import os

def get_whois_info(domain):
    try:
        # whois library might use system-wide proxy settings if set via environment variables
        w = whois.whois(domain)
        return w.text
    except Exception as e:
        return f"Error getting WHOIS info: {e}"

def get_dns_info(domain):
    results = {}
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'PTR']
    for rtype in record_types:
        try:
            # dnspython does not directly support proxies for DNS queries
            answers = dns.resolver.resolve(domain, rtype)
            results[rtype] = [str(rdata) for rdata in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            results[rtype] = []
        except Exception as e:
            results[rtype] = [f"Error: {e}"]

    # Check for SPF, DMARC, DKIM
    try:
        spf_records = dns.resolver.resolve(domain, 'TXT')
        results['SPF'] = [str(rdata) for rdata in spf_records if "v=spf1" in str(rdata)]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        results['SPF'] = []

    try:
        dmarc_records = dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
        results['DMARC'] = [str(rdata) for rdata in dmarc_records if "v=DMARC1" in str(rdata)]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        results['DMARC'] = []

    try:
        # Common DKIM selectors, can be expanded
        dkim_selectors = ['default', 'google', 'selector1', 'selector2']
        results['DKIM'] = []
        for selector in dkim_selectors:
            try:
                dkim_records = dns.resolver.resolve(f"{selector}._domainkey.{domain}", 'TXT')
                results['DKIM'].extend([str(rdata) for rdata in dkim_records if "v=DKIM1" in str(rdata)])
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
                pass
    except Exception as e:
        results['DKIM'] = [f"Error: {e}"]

    return results

def get_subdomains(domain, common_subdomains=None):
    if common_subdomains is None:
        common_subdomains = ['www', 'mail', 'ftp', 'blog', 'dev', 'test', 'api', 'admin', 'webmail', 'cpanel']

    found_subdomains = []
    for sub in common_subdomains:
        subdomain = f"{sub}.{domain}"
        try:
            # socket.gethostbyname does not directly support proxies
            socket.gethostbyname(subdomain)
            found_subdomains.append(subdomain)
        except socket.gaierror:
            pass # Subdomain does not exist
        except Exception as e:
            found_subdomains.append(f"{subdomain} (Error: {e})")
    return found_subdomains

def check_ssl_tls_versions(domain, port=443):
    supported_versions = []
    context = ssl.create_default_context()
    # Try to connect with different minimum TLS versions
    for min_version in [ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_3]:
        try:
            # Direct socket connections do not use HTTP/HTTPS proxies automatically
            with socket.create_connection((domain, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    supported_versions.append(ssock.version())
        except (ssl.SSLError, socket.timeout, ConnectionRefusedError):
            pass
        except Exception as e:
            supported_versions.append(f"Error checking {min_version.name}: {e}")
    return list(set(supported_versions)) # Return unique versions

def is_private_ip(ip_address):
    try:
        ip = ipaddress.ip_address(ip_address)
        return ip.is_private
    except ValueError:
        return False # Not a valid IP address

def analyze_domain(domain):
    results = {
        "whois": None,
        "dns": None,
        "subdomains": None,
        "ssl_tls_versions": None,
        "private_ip_warning": False
    }

    config = configparser.ConfigParser()
    config.read('config.ini')

    # Set environment variables for proxy, some libraries might pick them up
    if config.has_section('PROXY'):
        http_proxy = config['PROXY'].get('HTTP_PROXY')
        https_proxy = config['PROXY'].get('HTTPS_PROXY')
        if http_proxy: os.environ['HTTP_PROXY'] = http_proxy
        if https_proxy: os.environ['HTTPS_PROXY'] = https_proxy

    print(f"[*] Getting WHOIS info for {domain}...")
    results["whois"] = get_whois_info(domain)

    print(f"[*] Getting DNS info for {domain}...")
    dns_info = get_dns_info(domain)
    results["dns"] = dns_info

    # Check for private IPs in A and AAAA records
    for ip_list in [dns_info.get('A', []), dns_info.get('AAAA', [])]:
        for ip in ip_list:
            if is_private_ip(ip):
                results["private_ip_warning"] = True
                break
        if results["private_ip_warning"]:
            break

    print(f"[*] Searching for common subdomains for {domain}...")
    results["subdomains"] = get_subdomains(domain)

    print(f"[*] Checking SSL/TLS versions for {domain}...")
    results["ssl_tls_versions"] = check_ssl_tls_versions(domain)

    return results