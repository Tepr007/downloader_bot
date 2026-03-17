import subprocess
import sys

PARSERS = [
    "yt-dlp"
]

def update_parsers():
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        *PARSERS
    ]

    print("Updating parsers:", ", ".join(PARSERS))
    subprocess.run(cmd)

def main():
    try:
        print("Обновляем парсеры...")
        update_parsers()
        print("Парсеры успешно обновлены")
    except Exception as e:
        print(f"Ошибка при обновлении парсеров: {e}")