import os
import telebot
import json
import yt_dlp
import time
import threading

with open("DATA.json") as f:
    DATA = json.load(f)

FFMPEG_PATH = ".ffmpeg/bin/ffmpeg.exe"
FFMPEG_PARENT_PATH = ".ffmpeg/bin"
COOKIES_PATH = "cookies.txt"
bot = telebot.TeleBot(DATA["TOKEN"])



def loading_animation(chat_id, message_id, stop_event):
    dots = 1
    while not stop_event.is_set():
        text = "Скачиваю" + "." * dots
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
    print("Скачиваю...")
    download_msg = bot.send_message(message.chat.id, "Скачиваю.", reply_markup=None)

    stop_event = threading.Event()

    thread = threading.Thread(
        target=loading_animation,
        args=(bot, download_msg.chat.id, download_msg.message_id, stop_event)
    )
    thread.start()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(message.text, download=True)
            filepath = ydl.prepare_filename(info)
            with open(filepath, "rb") as f:
                bot.send_video(message.chat.id, f)
            os.remove(filepath)
        except Exception as e:
            print(e)
            error_text = "Не получилось скачать видео"
            bot.send_message(message.chat.id, error_text, reply_markup=None)
        finally:
            stop_event.set()
            thread.join()
            bot.delete_message(download_msg.chat.id, download_msg.message_id)


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()