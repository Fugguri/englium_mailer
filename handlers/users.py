from utils import user_bot
from aiogram import types
from aiogram import Dispatcher
from aiogram.dispatcher.handler import ctx_data
from aiogram.dispatcher import FSMContext

from utils import *
from config import Config
from db import Database
from keyboards.keyboards import Keyboards

import os
client_data = {}
user_active_clients = {}


async def start(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    markup = await kb.start_kb()

    try:
        await message.answer(cfg.misc.messages.start, reply_markup=markup)
    except:
        await message.message.edit_text(cfg.misc.messages.start, reply_markup=markup)

    await state.finish()

data = {}

selected_groups = {}
groups_list = None
all_groups = None
main_text = None


async def select_group(callback: types.CallbackQuery, callback_data: dict):
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    global selected_groups

    text = "Выберите группы для рассылки\n"
    if callback_data["id"] == "":
        global groups_list
        global all_groups
        if selected_groups:
            selected_groups = {}
        groups_list = await user_bot.get_chat_list()
        all_groups = await user_bot.get_chat_list()
    if callback_data["id"] != "":
        text += "Выбраны:\n"

        for group in groups_list:
            if str(group[1]) in selected_groups.keys():
                groups_list.pop(groups_list.index(group))
            if str(group[1]) == str(callback_data["id"]):
                groups_list.pop(groups_list.index(group))
                selected_groups[group[0]] = group
        for key, value in selected_groups.items():
            text += f"-{value[0]} ({value[3]})\n"

        markup = await kb.groups_kb(groups_list)
        await callback.message.edit_text(text, reply_markup=markup)
        return
    markup = await kb.groups_kb(groups_list)
    await callback.message.answer(text, reply_markup=markup)


async def start_mail(callback: types.CallbackQuery):
    kb: Keyboards = ctx_data.get()['keyboards']
    markup = await kb.start_kb()
    global selected_groups
    global main_text

    if not selected_groups:
        await callback.message.edit_text("Сначала выберите группы для рассылки", reply_markup=markup)
        return
    if not main_text:
        await callback.message.edit_text("Сначала введите текст рассылки", reply_markup=markup)
        return
    groups = selected_groups.values()
    recp = await user_bot.get_members_from_chats(groups)

    groups_text = ""
    counter = 1
    amount_mail_users = 0
    for _ in groups:
        amount_mail_users += _[3]
    for g in groups:
        groups_text += f"{counter}{g[0]}\n"
        counter += 1

    try:
        mes = await callback.message.answer(f"Начинаю рассылку по группам:\n{groups_text}Текст рассылки:{main_text}")
        # recp.add(("авыва", "423fsfsd5334dfgdfg", "564523423df"))
        res = await user_bot.start_mailing(recp, main_text)
        text = f"Доставлено ({len(res[0])} из {amount_mail_users}) :\n"

        for r in res[0]:
            text += f"{r[0]} {r[2]}\n"
        await callback.message.answer(text, reply_markup=markup)
        if len(res[1]) != 0:
            with open("mailing.txt", "w") as file:
                for r in res[1]:
                    file.write(f"{r}")

            with open("mailing.txt", "rb") as file:
                await callback.message.answer_document(file)
            os.system("rm mailing.txt")

    except Exception as ex:
        await callback.message.answer(f"Ошибка {ex} \nОбратитесь к администратору", reply_markup=markup)
    finally:
        await mes.delete()
        selected_groups = {}
        groups_list = None
        all_groups = None
        main_text = None


async def mail_text(callback: types.CallbackQuery, state: FSMContext):
    kb: Keyboards = ctx_data.get()['keyboards']

    markup = await kb.back_kb()
    await callback.message.edit_text("Отправьте текст рассылки", reply_markup=markup)
    await state.set_state("wait_mail_text")


async def wait_meil_text(message: types.Message):
    kb: Keyboards = ctx_data.get()['keyboards']

    global main_text
    main_text = message.text
    markup = await kb.back_kb()

    await message.answer(f"Чтобы изменить текст рассылки отправьте его еще раз.\nЕсли все верно нажмите кнопку назад\n<b>Текст рассылки:</b>\n{main_text}", reply_markup=markup)


async def contacts(message: types.Message):
    contacts = await user_bot.get_chat_id("fdsf")
    count = 1
    with open("contacts.txt", "w") as file:
        for r in contacts:
            file.write(f"{count}-{r}\n")
            count += 1
    with open("contacts.txt", "rb") as file:
        await message.answer_document(file)
    os.system("rm contacts.txt")


def register_user_handlers(dp: Dispatcher, cfg: Config, kb: Keyboards, db: Database):
    dp.register_message_handler(start, commands=["start"], state="*")
    dp.register_message_handler(contacts, commands=["contacts"], state="*")
    dp.register_callback_query_handler(start, kb.back_cd.filter(), state="*")

    dp.register_callback_query_handler(
        select_group, kb.select_group.filter(), state="*")
    dp.register_callback_query_handler(
        start_mail, lambda c: c.data == "start", state="*")
    dp.register_callback_query_handler(
        mail_text, lambda c: c.data == "mail_text", state="*")
    dp.register_message_handler(wait_meil_text, state="wait_mail_text")
