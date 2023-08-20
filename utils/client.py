import json
import asyncio
from helpers import DB
from telethon import TelegramClient, events, types

import telethon 






 
class UserBot:
    
    def __init__(self) -> None:
        with open("config.json", "rb") as file:
            data = json.load(file)
            self.api_id = data["api_id"]
            self.api_hash = data["api_hash"]
            self.phone = data["phone"]
        
        self.client = TelegramClient(self.phone, self.api_id, self.api_hash)

    # async def message(event):
    #     sender = await event.get_sender()
    
    async def get_chat_list(self):
        async with self.client:
            dialogs = await self.client.get_dialogs()
            result = []
            for d in dialogs:
                if type(d.message.peer_id) in (telethon.types.PeerChat,telethon.types.PeerChannel): 
                    result.append((d.name,d.id,d))
            return result

    async def get_members_from_chats(self,chats):
        part = ()
        async with self.client :
            for chat in chats:
                participants = await self.client.get_participants(chat[1])
                for p in participants:
                    print(p.name)
                    part.add(p)
                print(part)
                
    
                
if __name__ == "__main__":
    user_bot = UserBot()
    members = asyncio.run(user_bot.get_chat_list())
    print(members)
    asyncio.run(user_bot.get_members_from_chats(members))
