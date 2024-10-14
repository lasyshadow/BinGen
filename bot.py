import telebot
import random
import requests
import time
import os
import string

bot = telebot.TeleBot('BOT_TOKEN')


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


def generate_bin(card_type, length=6):
    """Generates a random bin number of the specified length."""

    valid_bins = {
        "VS": ["4026", "417500", "4508", "4844", "4913", "4917"],
        "MC": ["5100", "5105", "5218", "5222", "5312", "5482", "5555"],
        "AMEX": ["34", "37"],
        "DISC": ["6011", "622126", "644", "65"]
    }

    if card_type not in valid_bins:
        raise ValueError(
            "Invalid card type. Please choose from Visa, Mastercard, American Express, or Discover."
        )

    bin_prefix = random.choice(valid_bins[card_type])
    remaining_length = length - len(bin_prefix)
    remaining_digits = ''.join(
        random.choices(string.digits, k=remaining_length))
    bin_number = bin_prefix + remaining_digits

    return bin_number


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Welcome to the BIN checker bot! Use /check to check BINs from file, /gbin <card type> <amount> to generate BINs, or /gbintxt <card type> <amount> to generate BINs and receive them in a file."
    )


@bot.message_handler(commands=['check'])
def check_bin_command(message):
    try:
        with open('bins.txt', 'r') as f:
            bins = f.read().splitlines()

        valid_bins = []
        for bin_number in bins:
            bin_data = check_Bin(bin_number)
            if bin_data:
                response = f"BIN: {bin_data['bin']}\nScheme: {bin_data['scheme']}\nCountry: {bin_data['country']}\nType: {bin_data['type']}\nCategory: {bin_data['category']}\nBank: {bin_data['bank']}"
                valid_bins.append(response)

        if valid_bins:
            for response in valid_bins:
                bot.reply_to(message, response)
        else:
            bot.reply_to(message, "No valid BINs found in the file.")

    except FileNotFoundError:
        bot.reply_to(
            message,
            "Error: 'bins.txt' file not found. Please create it and add BINs to check."
        )


@bot.message_handler(commands=['gbin'])
def generate_bin_command(message):
    try:
        card_type, amount = message.text.split('/generate ', 1)[1].split()
        amount = int(amount)
        bins = [generate_bin(card_type.upper()) for _ in range(amount)]
        response = "\n".join(bins)
        bot.reply_to(message, response)
    except IndexError:
        bot.reply_to(
            message,
            "Please provide a card type and amount. Usage: /generate <card type> <amount>"
        )
    except ValueError as e:
        bot.reply_to(message, str(e))


@bot.message_handler(commands=['gbintxt'])
def generate_bin_file_command(message):
    try:
        card_type, amount = message.text.split('/gbintxt ', 1)[1].split()
        amount = int(amount)
        bins = [generate_bin(card_type.upper()) for _ in range(amount)]

        random_prefix = ''.join(random.choices(string.ascii_lowercase, k=3))
        user_id = message.from_user.id
        filename = f"{random_prefix}-{user_id}.txt"

        with open(filename, "w") as file:
            for bin_number in bins:
                file.write(bin_number + "\n")

        with open(filename, 'rb') as f:
            bot.send_document(message.chat.id, f)

        os.remove(filename)

    except IndexError:
        bot.reply_to(
            message,
            "Please provide a card type and amount. Usage: /generatefile <card type> <amount>"
        )
    except ValueError as e:
        bot.reply_to(message, str(e))


bot.polling()