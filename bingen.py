import random
import requests
import json
import threading
import time
from tqdm import tqdm

def generate_bin(card_type, custom_prefix=None):
    if custom_prefix:
        return custom_prefix
    if card_type == 'Visa':
        return '4' + ''.join([str(random.randint(0, 9)) for _ in range(5)])
    elif card_type == 'MasterCard':
        return str(random.choice([51, 52, 53, 54, 55])) + ''.join([str(random.randint(0, 9)) for _ in range(4)])
    elif card_type == 'American Express':
        return str(random.choice([34, 37])) + ''.join([str(random.randint(0, 9)) for _ in range(3)])
    elif card_type == 'Discover':
        return '6011' + ''.join([str(random.randint(0, 9)) for _ in range(2)])
    elif card_type == 'JCB':
        return '35' + ''.join([str(random.randint(0, 9)) for _ in range(4)])
    elif card_type == 'Diners Club':
        return str(random.choice([300, 301, 302, 303, 304, 305])) + ''.join([str(random.randint(0, 9)) for _ in range(2)])
    elif card_type == 'UnionPay':
        return '62' + ''.join([str(random.randint(0, 9)) for _ in range(4)])
    else:
        return None

def check_Bin(bin_number):
    url = f"https://binlist.io/lookup/{bin_number}"
    retries = 3
    while retries > 0:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        "bin": bin_number,
                        "scheme": data.get("scheme", "N/A"),
                        "country": data.get("country", {}).get("name", "N/A"),
                        "type": data.get("type", "N/A"),
                        "category": data.get("category", "N/A"),
                        "bank": data.get("bank", {}).get("name", "N/A")
                    }
            time.sleep(random.uniform(1, 3))
        except requests.exceptions.RequestException:
            retries -= 1
            time.sleep(random.uniform(1, 3))
    return None

def generate_bins(card_type, amount, custom_prefix=None):
    valid_bins = []
    
    def process_bin():
        bin_num = generate_bin(card_type, custom_prefix)
        if bin_num:
            bin_num += ''.join([str(random.randint(0, 9)) for _ in range(10 - len(bin_num))])
            bin_data = check_Bin(bin_num)
            if bin_data:
                valid_bins.append(bin_data)
    
    threads = []
    for _ in tqdm(range(amount), desc="Generating and checking BINs"):
        t = threading.Thread(target=process_bin)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    
    return valid_bins

def main():
    print("""
=====================
    BIN GENERATOR
=====================
    DEV - @XDPRO2
""")
    
    card_type = input("Enter card type (Visa, MasterCard, American Express, Discover, JCB, Diners Club, UnionPay): ").strip()
    custom_prefix = input("Enter a custom BIN prefix (or leave empty): ").strip()
    if custom_prefix == "":
        custom_prefix = None
    amount = int(input("Enter the number of BINs to generate: "))

    valid_bins = generate_bins(card_type, amount, custom_prefix)

    if valid_bins:
        filename = f"{card_type}-bins.txt"
        with open(filename, "w") as file:
            for bin_data in valid_bins:
                file.write(json.dumps(bin_data) + "\n")
        print(f"{len(valid_bins)} Valid Bina saved to {filename}.")
    else:
        print("No valid BINs generated.")
        
        if __name__ == '__main__':
        	main()
        	