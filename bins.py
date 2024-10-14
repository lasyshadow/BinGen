import random
import requests

def is_valid_bin(bin_number, card_type):
    """Checks the validity of a bin number using binlist.io API."""

    url = f"https://lookup.binlist.net/{bin_number}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data["scheme"] == card_type  # Check for specific card type
    else:
        return False

def generate_bin(card_type, length=6):
    """Generates a random bin number of the specified length."""

    valid_bins = {
        "VS": ["4", "51", "52", "53", "54", "55"],
        "MC": ["2221", "2222", "2223", "2224", "2225", "2226", "2227", "2228", "2229", "223", "224", "225", "226", "227", "228", "229", "23", "24", "25", "26", "27", "51", "52", "53", "54", "55"],
        "AMEX": ["34", "37"],
        "DISC": ["60", "64", "65"],
    }

    if card_type not in valid_bins:
        raise ValueError("Invalid card type. Please choose from Visa, Mastercard, American Express, or Discover.")

    bin_prefix = random.choice(valid_bins[card_type])
    remaining_digits = "0" * (length - len(bin_prefix))
    bin_number = bin_prefix + remaining_digits

    # Shuffle remaining digits for better randomness (optional)
    remaining_digits = list(remaining_digits)
    random.shuffle(remaining_digits)
    shuffled_bin = bin_prefix + "".join(remaining_digits)

    return shuffled_bin  # Use shuffled_bin for better randomness

def main():
    """Prompts user for input, generates and checks bins, and saves valid ones to a file."""

    card_type = input("Enter card type (Visa, Mastercard, American Express, or Discover): ").upper()
    num_bins = int(input("Enter the number of bins to generate: "))

    valid_bins = []
    for _ in range(num_bins):
        bin_number = generate_bin(card_type)
        if is_valid_bin(bin_number, card_type):
            valid_bins.append(bin_number)

    if valid_bins:
        filename = f"{card_type}_bins_{num_bins}.txt"
        with open(filename, "w") as file:
            file.write("\n".join(valid_bins))
        print(f"Successfully saved {len(valid_bins)} valid bins to {filename}")
    else:
        print(f"No valid bins found for {card_type} after {num_bins} attempts.")

if __name__ == "__main__":
    main()
