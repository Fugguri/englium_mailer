from aiogram import types
from aiogram import Dispatcher
from aiogram.dispatcher.handler import ctx_data
from aiogram.dispatcher import FSMContext
import telethon
from utils import *
from config import Config
from db import Database
from keyboards.keyboards import Keyboards
from utils.userBot import UserBot
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
entities = None


async def select_group(callback: types.CallbackQuery, callback_data: dict):
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    userbot = ctx_data.get()['user_bot']
    global selected_groups

    text = "Выберите группы для рассылки.\nЕсли ошиблись в выборе выйдите в главное меню и начните заново!"
    if callback_data["id"] == "":
        global groups_list
        global all_groups
        if selected_groups:
            selected_groups = {}
        groups_list = await userbot.get_chat_list()
        all_groups = await userbot.get_chat_list()
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


async def mail_all(callback: types.CallbackQuery, state: FSMContext):
    kb: Keyboards = ctx_data.get()['keyboards']
    markup = await kb.is_all_mail()
    global main_text
    if not main_text:
        markup = await kb.start_kb()
        await callback.message.edit_text("Сначала введите текст рассылки", reply_markup=markup)
        return
    await callback.message.answer("Повторять отправку сообщений ?", reply_markup=markup)


async def start_mail(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    kb: Keyboards = ctx_data.get()['keyboards']
    markup = await kb.start_kb()
    user_bot: UserBot = ctx_data.get()['user_bot']
    global selected_groups

    if not selected_groups:
        await callback.message.edit_text("Сначала выберите группы для рассылки", reply_markup=markup)
        return
    global main_text
    if not main_text:
        await callback.message.edit_text("Сначала введите текст рассылки", reply_markup=markup)
        return
    groups = selected_groups.values()
    recp = await user_bot.get_members_from_chats(groups)

    await callback.message.delete()
    if callback_data['all'] == "False":
        numbers = []
        re = []
        for x in recp:
            print(x)
            if x[1] not in numbers:
                numbers.append(x[1])
                re.append(x)
        recp = re
    groups_text = ""
    counter = 1
    amount_mail_users = 0
    for _ in groups:
        amount_mail_users += _[3]
    for g in groups:
        groups_text += f"{counter}. {g[0]}\n"
        counter += 1

    try:
        user_bot.stop_mailing = False
        mes = await callback.message.answer(f"Начинаю рассылку по группам:\n{groups_text}Текст рассылки:{main_text}")
        res = await user_bot.start_mailing(recp, main_text)
        text = f"Не доставлено ({len(res[0])} из {amount_mail_users}) :\n"

        if len(res[1]) != 0:
            with open("mailing.txt", "w") as file:
                for r in res[1]:
                    file.write(f"{r}")

            with open("mailing.txt", "rb") as file:
                await callback.message.answer_document(file, caption=text)
            os.system("rm mailing.txt")
        else:
            await callback.message.answer(f"Доставлено ({len(res[0])} из {amount_mail_users})\nГруппы для рассылки:\n{groups_text}")
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
    user_bot: UserBot = ctx_data.get()['user_bot']
    global main_text
    global entities
    main_text = message.html_text
    markup = await kb.back_kb()
    if message.entities:
        entities = []
        for ent in message.entities:
            entities.append(
                telethon.types.TypeMessageEntity(ent.offset, ent.length, ent.custom_emoji_id))
        print(entities)
        await message.answer(f"Чтобы изменить текст рассылки отправьте его еще раз.\nЕсли все верно нажмите кнопку назад\n<b>Текст рассылки:</b>\n{main_text}",
                             entities=entities,
                             reply_markup=markup)
        async with user_bot.client:
            await user_bot.client.send_message("fugguri", message=main_text, parse_mode="HTML", formatting_entities=entities)
        return
    await message.answer(f"Чтобы изменить текст рассылки отправьте его еще раз.\nЕсли все верно нажмите кнопку назад\n<b>Текст рассылки:</b>\n{main_text}", reply_markup=markup)


async def contacts(callback: types.CallbackQuery):
    db: Database = ctx_data.get()['db']
    user_bot: UserBot = ctx_data.get()['user_bot']

    mes = await callback.message.answer("Начинаю обновление")
    try:
        contacts = await user_bot.get_chat_id("fdsf")
        count = 1
        with open("contacts.txt", "w") as file:
            for r in contacts:
                db.add_contact(*r)
                file.write(f"{count}-{r}\n")
                count += 1
        with open("contacts.txt", "rb") as file:
            await callback.message.answer_document(file)
        os.system("rm contacts.txt")
    except Exception as ex:
        await callback.message.answer(f"Ошибка {ex}")
    finally:
        await mes.delete()


async def stop(callback: types.CallbackQuery):
    db: Database = ctx_data.get()['db']
    kb: Keyboards = ctx_data.get()['keyboards']
    user_bot: UserBot = ctx_data.get()['user_bot']

    mes = await callback.message.answer("Останавливаю")

    try:
        user_bot.stop_mailing = True
        user_bot.stop_remaining = True

    except Exception as ex:
        await callback.message.answer(f"Ошибка {ex}")

    finally:
        await mes.delete()
        await callback.message.answer("Остановил",)


async def remain_all(callback: types.CallbackQuery, state: FSMContext):
    kb: Keyboards = ctx_data.get()['keyboards']
    markup = await kb.is_all()
    global main_text
    if not main_text:
        markup = await kb.start_kb()
        await callback.message.edit_text("Сначала введите текст рассылки", reply_markup=markup)
        return
    await callback.message.answer("Отправлять сообщения при повторе номера?", reply_markup=markup)


async def answer(message: types.Message):
    await message.answer(str(message))


async def remaining(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    db: Database = ctx_data.get()['db']
    kb: Keyboards = ctx_data.get()['keyboards']
    user_bot: UserBot = ctx_data.get()['user_bot']

    res = google_sheets.collect_data()
    markup = await kb.start_kb()
    global main_text
    if res == []:
        await callback.message.edit_text("Нет отмеченных для рассылки контактов", reply_markup=markup)
        main_text = None
        return

    if callback_data['all'] == "False":
        numbers = []
        re = []
        for x in res:
            if x[3] not in numbers:
                numbers.append(x[3])
                re.append(x)
        res = re

    amount_mail_users = len(res)
    mes = await callback.message.answer("Начинаю рассылку")
    try:
        user_bot.stop_remaining = False
        senders = await user_bot.remain(res, db, main_text)
        if len(senders[1]) != 0:
            not_send_text = ""
            with open("mailing.txt", "w") as file:
                for r in senders[1]:
                    file.write(f"{r[:7]}")
                    not_send_text += str(r)+"\n"
            with open("mailing.txt", "rb") as file:
                await callback.message.answer_document(file, caption="Не доставлено\n")
            os.system("rm mailing.txt")
        await callback.message.answer(f"Доставлено ({len(senders[0])} из {amount_mail_users})\n")
    except Exception as ex:
        await callback.message.answer(f"Ошибка {ex}")
    finally:
        main_text = None
        await mes.delete()


def register_user_handlers(dp: Dispatcher, cfg: Config, kb: Keyboards, db: Database):
    dp.register_message_handler(start, commands=["start"], state="*")

    dp.register_callback_query_handler(
        contacts, lambda c: c.data == "contacts", state="*")

    dp.register_callback_query_handler(
        remain_all, lambda c: c.data == "remainder", state="*")
    dp.register_callback_query_handler(
        mail_all, lambda c: c.data == "mail", state="*")

    dp.register_callback_query_handler(
        remaining, kb.remain_cd.filter(), state="*")
    dp.register_callback_query_handler(
        start_mail, kb.mail_cd.filter(), state="*")

    dp.register_callback_query_handler(start, kb.back_cd.filter(), state="*")

    dp.register_callback_query_handler(
        select_group, kb.select_group.filter(), state="*")

    dp.register_callback_query_handler(
        stop, lambda c: c.data == "stop", state="*")

    dp.register_callback_query_handler(
        mail_text, lambda c: c.data == "mail_text", state="*")
    dp.register_message_handler(wait_meil_text, state="wait_mail_text")
    dp.register_message_handler(answer)
