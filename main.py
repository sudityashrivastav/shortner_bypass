import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import re

BOT_TOKEN = "6456014340:AAEsM0raVSet_RqKtOpcG83SGbvVD1YkhUk"

bot = telebot.TeleBot(BOT_TOKEN)
# episode_links = []


@bot.message_handler(commands=['start'])
def show_buttons(message):
    bot.reply_to(message, "Share the link!")


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    base_url = message.text
    if base_url.startswith("https") == False: 
        return bot.reply_to(message, "Please send link only")
    bot.reply_to(message, "Please wait...")

    headers = {
        'Host': 'Techmny.com',
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"
    }

    response_1 = requests.get(base_url)
    soup_1 = BeautifulSoup(
        response_1.content, "html.parser").find_all("meta")[1]
    redirect_url = soup_1.get("content").replace("0;url=", "")
    response_2 = requests.get(redirect_url)
    episode_links = BeautifulSoup(
        response_2.content, "html.parser").find_all("a")

    if len(episode_links) > 1:
        episode_links = episode_links[1:-5]

        print("Select Episode: ", len(episode_links))

        array_length = len(episode_links)
        if array_length > 1:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            buttons = [telebot.types.InlineKeyboardButton(f"Episode {i + 1}", callback_data=str(i)) for i in range(array_length)]
            keyboard.add(*buttons)

            bot.send_message(message.chat.id, "Select episode: ", reply_markup=keyboard)
        
        @bot.callback_query_handler(func=lambda call: True)
        def handle_button_callback(call):
            selected_index = int(call.data)
            bot.send_message(call.message.chat.id, f"You selected: {selected_index + 1}")

            selected_episode = episode_links[selected_index]
            bot.send_message(call.message.chat.id, "Please wait...")


            response_3 = requests.get(selected_episode["href"])


            post_value = BeautifulSoup(response_3.content, "html.parser").find("input")["value"]

            post_data = {
                "_wp_http": post_value
            }

            response_4 = requests.post("https://techmny.com/", headers=headers, data=post_data)
            form_action = BeautifulSoup(response_4.content, "html.parser").find("form")["action"]
            input_fields = BeautifulSoup(response_4.content, "html.parser").find_all("input")
            post_value_2 = input_fields[0]["value"]
            post_token = input_fields[1]["value"]

            post_data_2 = {
                "_wp_http2": post_value_2,
                "token": post_token
            }

            html_content = requests.post(form_action, headers=headers, data=post_data_2).text

            pattern1 = r"sk-64(.*?)'"
            pattern2 = r"eJw(.*?)'"

            match1 = re.search(pattern1, html_content)
            match2 = re.search(pattern2, html_content)

            if match1 and match2:
                string_value1 = "sk-64" + match1.group(1)
                string_value2 = "eJw" + match2.group(1)
                headers_v2 = {
                    "Host": "Techmny.com",
                    "Cookie": string_value1 + "=" + string_value2,
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"
                }

                final_response = requests.get(f"https://techmny.com/?go={string_value1}", headers=headers_v2)
                final_url = BeautifulSoup(final_response.text, "html.parser").find_all("meta")[1]["content"].replace("0;url=", "")

                downloadKeyboard = telebot.types.InlineKeyboardMarkup()
    
                # Create an inline keyboard button with a link
                button = telebot.types.InlineKeyboardButton("Download Now", url=final_url)
                downloadKeyboard.add(button)
                bot.send_message(call.message.chat.id, "Bypassed Succesfully",reply_markup=downloadKeyboard)
                exit()
            else:
                bot.send_message(call.message.chat.id, "not found")




bot.infinity_polling()