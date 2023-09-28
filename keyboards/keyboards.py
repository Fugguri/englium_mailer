from config import Config
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
    ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton


class Keyboards:
    def __init__(self, cfg: Config) -> None:
        self.text = cfg.misc.buttons_texts
        self.add_profile_cd = CallbackData("add_profile", "level")
        self.select_group = CallbackData("select_group", "id")
        self.remain_cd = CallbackData("remain", "all")
        self.mail_cd = CallbackData("mail", "all")
        self.back_cd = CallbackData("back")

    async def start_kb(self, user_id=None):
        add_profile = self.text.add_profile
        edit_profile = self.text.edit_profile

        kb = InlineKeyboardMarkup(row_width=3)

        kb.add(InlineKeyboardButton(text=add_profile,
               callback_data=self.select_group.new(id="")))
        kb.add(InlineKeyboardButton(text=edit_profile, callback_data="mail_text"))
        kb.add(InlineKeyboardButton(
            text="Начать рассылку(из групп)", callback_data="mail"))
        kb.add(InlineKeyboardButton(
            text="Обновить контакты", callback_data="contacts"))
        kb.add(InlineKeyboardButton(
            text="Начать рассылку(гугл таблицы)", callback_data="remainder"))
        kb.add(InlineKeyboardButton(
            text="Csv файл", callback_data="file"))
        kb.add(InlineKeyboardButton(
            text="Остановить рассылки", callback_data="stop"))

        return kb

    async def is_all(self):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text="С повторами",
               callback_data=self.remain_cd.new(all=True)))
        kb.add(InlineKeyboardButton(text="Без повторов",
               callback_data=self.remain_cd.new(all=False)))
        kb.add(InlineKeyboardButton(text="Назад",
               callback_data=self.back_cd.new()))
        return kb

    async def is_all_mail(self):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text="С повторами",
               callback_data=self.mail_cd.new(all=True)))
        kb.add(InlineKeyboardButton(text="Без повторов",
               callback_data=self.mail_cd.new(all=False)))
        kb.add(InlineKeyboardButton(text="Назад",
               callback_data=self.back_cd.new()))
        return kb

    async def groups_kb(self, groups):
        kb = InlineKeyboardMarkup()

        for group in groups:
            kb.add(InlineKeyboardButton(
                text=f"{group[0]} ({group[3]})", callback_data=self.select_group.new(id=group[1])))
        kb.add(InlineKeyboardButton(text="Назад",
               callback_data=self.back_cd.new()))
        return kb

    async def back_kb(self):
        kb = InlineKeyboardMarkup()

        kb.add(InlineKeyboardButton(text="Назад",
               callback_data=self.back_cd.new()))

        return kb
