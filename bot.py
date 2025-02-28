import discord
import requests
import asyncio
from datetime import datetime, timedelta

TOKEN = "TON_DISCORD_BOT_TOKEN"
USER_ID = TON_ID_UTILISATEUR_DISCORD
API_URL = "https://api.idlesteam.com/status"
CHECK_INTERVAL = 60  # Vérification toutes les 60 secondes
OFFLINE_THRESHOLD = 20 * 60  # 20 minutes en secondes

offline_since = None

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Connecté en tant que {self.user}')
        await self.check_api_status()

    async def check_api_status(self):
        global offline_since
        
        while True:
            try:
                response = requests.get(API_URL, timeout=5)
                if response.status_code == 200:
                    if offline_since:
                        print("L'API est de nouveau en ligne.")
                    offline_since = None
                else:
                    if not offline_since:
                        offline_since = datetime.utcnow()
                    elif (datetime.utcnow() - offline_since).total_seconds() > OFFLINE_THRESHOLD:
                        await self.notify_user()
                        offline_since = None  # Pour éviter les messages répétés
            except requests.RequestException:
                if not offline_since:
                    offline_since = datetime.utcnow()
                elif (datetime.utcnow() - offline_since).total_seconds() > OFFLINE_THRESHOLD:
                    await self.notify_user()
                    offline_since = None
            
            await asyncio.sleep(CHECK_INTERVAL)

    async def notify_user(self):
        user = await self.fetch_user(USER_ID)
        if user:
            try:
                await user.send("L'API IdleSteam est hors ligne depuis plus de 20 minutes !")
                print("Message envoyé à l'utilisateur.")
            except discord.Forbidden:
                print("Impossible d'envoyer un message privé.")
        else:
            print("Utilisateur introuvable.")

intents = discord.Intents.default()
client = MyClient(intents=intents)
client.run(TOKEN)
