import os
import telebot
import json
import yt_dlp
import time
import threading

import update_parsers

with open("DATA.json") as f:
    DATA = json.load(f)

FFMPEG_PATH = ".ffmpeg/bin/ffmpeg.exe"
FFMPEG_PARENT_PATH = ".ffmpeg/bin"
COOKIES_PATH = "cookies.txt"
bot = telebot.TeleBot(DATA["TOKEN"])

print('='*40)
print(f"{'Video Downloader':^40}")
print('='*40)

update_parser = threading.Timer(3600, update_parsers.main)
update_parser.start()

def loading_animation(chat_id, message_id, stop_event, title):
    dots = 1
    while not stop_event.is_set():
        text = f"Скачиваю {title}" + "." * dots
        try:
            bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=message_id
            )
        except:
            pass
        dots = dots % 3 + 1
        time.sleep(1)

@bot.message_handler(commands=["start"])
def start(message):
    start_text = f"""Отправьте ссылку на видео чтобы скачать 
Бот поддерживает не только YouTube, VK и TikTok 
Поддерживамых сайтов гигантское множество 
Чтобы проверить, поддерживает ли бот скачивание с того или иного сайта, пришлите ссылку на видео
Бот работает на библиотеке yt-dlp и его код можно найти на GitHub <a href="{DATA["GitHub"]}">по ссылке</a>
Автор: @tepr007"""
    bot.send_message(message.chat.id, start_text, reply_markup=None, parse_mode="HTML")

@bot.message_handler()
def Enter(message):
    ydl_opts = {
        "cookies": COOKIES_PATH,
        "format": "bestvideo+bestaudio/best",
        "quiet": True,
        "ffmpeg_location": FFMPEG_PARENT_PATH,
        "writethumbnail": True,
        "merge_output_format": "mp4",
        "postprocessors": [
            {
                "key": "EmbedThumbnail",
            },
            {
                "key": "FFmpegMetadata",
            },
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(message.text, download=False)

            # if info["filesize"] > 50 * 1024 * 1024:
            #     bot.send_message(message.chat.id, "Видео слишком большое")
            #     return
        except Exception as e:
            print(e)
            error_text = "Не получилось скачать видео"
            bot.send_message(message.chat.id, error_text, reply_markup=None)
            return

    print(f"Скачиваю {info['title']}...")
    download_msg = bot.send_message(message.chat.id, f"Скачиваю {info['title']}.", reply_markup=None)

    stop_event = threading.Event()

    thread = threading.Thread(
        target=loading_animation,
        args=(download_msg.chat.id, download_msg.message_id, stop_event, info['title'])
    )
    thread.start()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        filepath = None
        try:
            info = ydl.extract_info(message.text, download=True)
            filepath = ydl.prepare_filename(info)
            with open(filepath, "rb") as f:
                bot.send_video(message.chat.id, f)
            os.remove(filepath)
            answer = "Видео скачено"
            bot.edit_message_text(answer,
                chat_id=download_msg.chat.id,
                message_id=download_msg.message_id
            )
            stop_event.set()
            thread.join()
        except Exception as e:
            if filepath != None and os.path.exists(filepath):
                os.remove(filepath)
            print(e)
            stop_event.set()
            thread.join()
            error_text = "Не получилось скачать видео"
            bot.edit_message_text(error_text,
                chat_id=download_msg.chat.id,
                message_id=download_msg.message_id
            )


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()