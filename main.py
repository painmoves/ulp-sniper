import os
import shutil
import time
import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument
from discord_webhook import DiscordWebhook

# === CONFIGURATION ===
API_ID = 
API_HASH = ""
SESSION_NAME = ""
CHANNEL_ID = 
PHONE = ""
WEBHOOK_URL = ""  


BASE_PATH = ""  
TARGET_FOLDERS = {
    'discord': os.path.join(BASE_PATH, 'discord'), #will scan for "discord" word and if found it will download in the base path + this target folder and if it doesnt find the keyword it will simply be downloaded in the downloads folder
}


DOWNLOADS_LOG = os.path.join(BASE_PATH, "downloads.txt")


client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


def send_to_discord(message):
    webhook = DiscordWebhook(url=WEBHOOK_URL, content=message)
    webhook.execute()
    print(f"Message envoyé au webhook: {message}")


def is_file_downloaded(filename):
    if not os.path.exists(DOWNLOADS_LOG):
        return False
    with open(DOWNLOADS_LOG, "r") as log_file:
        downloaded_files = log_file.readlines()
        return filename + "\n" in downloaded_files


def mark_file_as_downloaded(filename):
    with open(DOWNLOADS_LOG, "a") as log_file:
        log_file.write(filename + "\n")


async def download_file(message, filename):
    if is_file_downloaded(filename):
        print(f"Le fichier {filename} a déjà été téléchargé. Ignoré.")
        return

    send_to_discord(f"# Le fichier {filename} est en ajout! :rocket:")

    target_folder = TARGET_FOLDERS['urlpass'] 

    if 'discord' in filename.lower():
        target_folder = TARGET_FOLDERS['discord']
    elif 'doxbin' in filename.lower():
        target_folder = TARGET_FOLDERS['doxbin']
    elif 'database' in filename.lower():
        target_folder = TARGET_FOLDERS['database']
    elif 'db' in filename.lower():
        target_folder = TARGET_FOLDERS['db']


    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"Dossier {target_folder} créé.")

    file_path = os.path.join(target_folder, filename) 

    print(f"Téléchargement du fichier {filename} dans {target_folder}...")
    await message.download_media(file=file_path)


    if os.path.exists(file_path):
        print(f"Fichier {filename} téléchargé avec succès dans {target_folder}.")
        mark_file_as_downloaded(filename)  
        send_to_discord(f"# Ajouté sans probleme!")
    else:
        print(f"Erreur: Le fichier {filename} n'a pas été téléchargé.")

async def check_new_files():
    await client.start(PHONE)

    async for message in client.iter_messages(CHANNEL_ID):
        if message.media: 
            if isinstance(message.media, MessageMediaDocument): 
                filename = message.file.name
                print(f"Fichier détecté: {filename}")

                if filename.endswith(".txt"):
                    await download_file(message, filename)

    await client.disconnect()

while True:
    time.sleep(2) 
    asyncio.run(check_new_files())  
