import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def probe(host, timeout=3):
    protocols = ['http://', 'https://']
    results = []
    for protocol in protocols:
        try:
            url = f"{protocol}{host}"
            response = requests.get(url, timeout=timeout)
            if response.status_code < 400:
                results.append(url)
        except requests.exceptions.RequestException:
            pass
    return results

def probe_all_hosts(hosts, timeout=3, workers=10):
    unique_results = set()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(probe, host, timeout): host for host in hosts}
        for future in as_completed(futures):
            urls = future.result()
            for url in urls:
                unique_results.add(url)
    return sorted(unique_results)

def main():
    parser = argparse.ArgumentParser(description="Probe a list of hosts for HTTP and HTTPS")
    parser.add_argument("input_file", help="Path to input file containing one host per line")
    parser.add_argument("-t", "--timeout", type=int, default=3, help="Timeout for each request in seconds (default: 3)")
    parser.add_argument("-w", "--workers", type=int, default=10, help="Number of worker threads (default: 10)")

    args = parser.parse_args()

    with open(args.input_file, "r") as f:
        hosts = [line.strip() for line in f.readlines()]

    results = probe_all_hosts(hosts, timeout=args.timeout, workers=args.workers)

    for result in results:
        print(result)

if __name__ == "__main__":
    main()
