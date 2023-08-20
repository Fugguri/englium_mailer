from config import Config
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
    ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton


class Keyboards:
    def __init__(self, cfg: Config) -> None:
        self.text = cfg.misc.buttons_texts
        self.add_profile_cd = CallbackData("add_profile", "level")
        self.client_data_cd = CallbackData(
            "add_profile", "phone", "api_id", "api_hash", "code_hash")
        self.black_list_cd = CallbackData("black_list", "level")
        self.edit_client_cd = CallbackData(
            "edit_client", "user_id", "client_id", "command")
        self.manual_mailing_cd = CallbackData(
            "manual_mailing", "user_id", "client_id", "command")
        self.start_receiving_cd = CallbackData(
            "start_receiving", "user_id", "client_id", "command")
        self.copy_settings_cd = CallbackData(
            "copy_settings", "user_id", "client_id", "command")

        self.back_cd = CallbackData("back")

    async def start_kb(self, user_id=None):
        add_profile = self.text.add_profile
        edit_profile = self.text.edit_profile

        kb = InlineKeyboardMarkup()

        kb.add(InlineKeyboardButton(text=add_profile,
               callback_data=self.add_profile_cd.new(level="0")))
        kb.add(InlineKeyboardButton(text=edit_profile, callback_data=self.edit_client_cd.new(
            user_id="", client_id="", command="")))

        return kb

    async def admin_kb(self):
        kb = InlineKeyboardMarkup()

        kb.add(InlineKeyboardButton(
            text="Дать доступ", callback_data="access grand"))
        kb.add(InlineKeyboardButton(
            text="Прекратить доступ", callback_data="access denied"))
        kb.add(InlineKeyboardButton(text="Назад",
               callback_data=self.back_cd.new()))

        return kb

    async def client_kb(self, level):
        kb = InlineKeyboardMarkup()

        kb.add(InlineKeyboardButton(text="Далее",
               callback_data=self.add_profile_cd.new(level=level)))

        return kb

    async def edit_client_kb(self, clients=None, user_id=None, client_id=None):
        kb = InlineKeyboardMarkup()

        if clients != None:
            for client in clients:
                kb.add(InlineKeyboardButton(text=client.phone,
                                            callback_data=self.edit_client_cd.new(user_id="",
                                                                                  client_id=client.id,
                                                                                  command="")))
            kb.add(InlineKeyboardButton(text="Назад",
                   callback_data=self.back_cd.new()))
            return kb

        if client_id != None:

            kb.add(InlineKeyboardButton(text="Настройка ИИ", callback_data=self.edit_client_cd.new(
                user_id=user_id, client_id=client_id, command="AI")))
            kb.add(InlineKeyboardButton(text="Текст сообщения", callback_data=self.edit_client_cd.new(
                user_id=user_id, client_id=client_id, command="text")))
            kb.add(InlineKeyboardButton(text="Настройки статистики", callback_data=self.edit_client_cd.new(
                user_id=user_id, client_id=client_id, command="stat")))
            kb.add(InlineKeyboardButton(text="Вся информация", callback_data=self.edit_client_cd.new(
                user_id=user_id, client_id=client_id, command="info")))
            kb.add(InlineKeyboardButton(text="Назад",
                   callback_data=self.back_cd.new()))

        return kb

    async def start_receive_kb(self, clients=None, user_id=None):
        kb = InlineKeyboardMarkup()

        if clients != None:
            for client in clients:
                kb.add(InlineKeyboardButton(text=client.phone,
                                            callback_data=self.start_receiving_cd.new(user_id=user_id,
                                                                                      client_id=client.id,
                                                                                      command="")))
            kb.add(InlineKeyboardButton(text="Назад",
                   callback_data=self.back_cd.new()))
            return kb

        return kb

    async def copy_settings_kb(self, clients=None, user_id=None):
        kb = InlineKeyboardMarkup()

        if clients != None:
            for client in clients:
                kb.add(InlineKeyboardButton(text=client.phone,
                                            callback_data=self.copy_settings_cd.new(user_id=user_id,
                                                                                    client_id=client.id,
                                                                                    command="")))
            kb.add(InlineKeyboardButton(text="Назад",
                   callback_data=self.back_cd.new()))
            return kb

        return kb

    async def manual_mailing_kb(self, clients=None, user_id=None):
        kb = InlineKeyboardMarkup()

        if clients != None:
            for client in clients:
                kb.add(InlineKeyboardButton(text=client.phone,
                                            callback_data=self.manual_mailing_cd.new(user_id=user_id,
                                                                                     client_id=client.id,
                                                                                     command="")))
            kb.add(InlineKeyboardButton(text="Назад",
                   callback_data=self.back_cd.new()))
            return kb

        return kb

    async def back_kb(self):
        kb = InlineKeyboardMarkup()

        kb.add(InlineKeyboardButton(text="Назад",
               callback_data=self.back_cd.new()))

        return kb
