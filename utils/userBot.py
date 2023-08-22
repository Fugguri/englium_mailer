import json
import asyncio
from telethon import TelegramClient, events, types

import telethon


class UserBot:

    def __init__(self) -> None:
        with open("config.json", "rb") as file:
            data = json.load(file)
            self.api_id = data["api_id"]
            self.api_hash = data["api_hash"]
            self.phone = data["phone"]
            self.teachers = data["teachers_list"]
        self.client = TelegramClient(
            "sessions/"+self.phone, self.api_id, self.api_hash)

    # async def message(event):
    #     sender = await event.get_sender()

    async def get_chat_list(self):
        async with self.client:
            dialogs = await self.client.get_dialogs()
            result = []
            for d in dialogs:
                if type(d.entity) == types.ChatForbidden:
                    continue
                if type(d.message.peer_id) in (telethon.types.PeerChat, telethon.types.PeerChannel):
                    result.append(
                        (d.name, d.id, d, d.entity.participants_count))
                participants = await self.client.get_participants(d.id)
                for p in participants:
                    print(
                        (p.username, p.id, f"{p.first_name} {p.last_name}", len(participants)))

        return result

    async def get_chat_id(self, phone_num):
        import tempfile
        from telethon.client.telegramclient 
        temp_contact_name = tempfile.NamedTemporaryFile().name.split('\\')[-1]
        good_res = list()
        async with self.client:
            self.client.import_contacts(
                [types.InputPhoneContact(phone=phone_num, first_name=temp_contact_name)])
            contacts = self.client.get_contacts()
            for contact in contacts:
                contact_data = json.loads(str(contact))
                if contact_data['first_name'] == temp_contact_name:
                    good_res.append(contact_data)
                    self.client.delete_contacts(contact_data['id'])
        try:
            good_res = good_res[0]['id']
        except:
            good_res = None
        return good_res

    async def get_members_from_chats(self, chats):
        part = set()
        async with self.client:
            for chat in chats:
                participants = await self.client.get_participants(chat[1])
                for p in participants:
                    part.add(
                        (p.username, p.id, f"{p.first_name} {p.last_name}", len(participants)))
        return part

    async def start_mailing(self, recepients, text=None):
        counter = 0
        send = []
        not_send = []
        async with self.client:
            for rec in recepients:
                if counter <= 10:
                    try:
                        if rec[1] not in self.teachers:
                            await self.client.send_message(rec[1], text)
                            send.append(rec)
                        else:
                            not_send.append(rec)
                            
                    except Exception as ex:
                        print(ex)
                        not_send.append(rec)

                    counter += 1
                else:
                    await asyncio.sleep(60)
                    try:
                        if rec[1] not in self.teachers:
                            await self.client.send_message(rec[1], text)
                            send.append(rec)
                        else:
                            not_send.append(rec)

                    except Exception as ex:
                        print(ex)
                        not_send.append(rec)
                    counter = 0
        return send, not_send


if __name__ == "__main__":
    cl = UserBot()
    print(asyncio.run(cl.get_chat_id("+79167352614")))
