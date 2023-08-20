from aiogram import types
from aiogram import Dispatcher
from aiogram.dispatcher.handler import ctx_data
from aiogram.dispatcher import FSMContext

from utils import *
from config import Config
from DB_connectors import Database
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
        await message.message.answer(cfg.misc.messages.start, reply_markup=markup)

    await state.finish()


async def help(callback: types.CallbackQuery):
    kb: Keyboards = ctx_data.get()['keyboards']
    markup = await kb.back_kb()
    await callback.message.answer(
        text="Ссылка на инструкцию по регистрации https://telegra.ph/Instrukciya-po-registracii-03-25 ", reply_markup=markup)


async def pay(callback: types.CallbackQuery):
    kb: Keyboards = ctx_data.get()['keyboards']
    markup = await kb.back_kb()
    try:
        await callback.message.answer(text="Для получения доступа - напишите @son2421", reply_markup=markup)
    except:
        await callback.answer(text="Для получения доступа - напишите @son2421", reply_markup=markup)


async def copy_settings(callback: types.CallbackQuery, callback_data: dict):
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.back_kb()

    user_id = callback_data["user_id"]
    client_id = callback_data["client_id"]
    command = callback_data["command"]

    clients = db.get_clients(user_id)
    markup = await kb.copy_settings_kb(user_id=user_id, clients=clients)

    if not clients:
        await callback.message.answer('Сначала добавьте профиль в разделе "Добавить профиль"', reply_markup=markup)
        return

    if user_id != "" and client_id == "":
        markup = await kb.copy_settings_kb(user_id=user_id, clients=clients)
        await callback.message.answer("Выберите номер c которого копируем данные.\nЕсли в списке нет номеров, добавьте их в главном меню!", reply_markup=markup)
        return

    if client_id != "" and command == "":
        client = db.get_client(client_id)
        if not client.ai_settings:
            markup = await kb.back_kb()
            await callback.message.answer('Сначала настройте бота в разделе "Редактировать профиль"', reply_markup=markup)
            return
        try:
            db.update_all_clients(client_id, user_id)
            markup = await kb.back_kb()
            await callback.message.answer("Скопировал данные", reply_markup=markup)
        except Exception as ex:
            print(ex)


async def wait_mailing_base(callback: types.CallbackQuery, state: FSMContext):
    db: Database = ctx_data.get()['db']
    kb: Keyboards = ctx_data.get()['keyboards']

    markup = await kb.back_kb()

    user = db.get_user(callback.from_user.id)

    if not user.has_access:
        await pay(callback)
        return

    await state.set_state("wait mailing base")

    await callback.message.answer(text="Отправьте список usename для рассылки.", reply_markup=markup)


async def collect_mailing_base(message: types.Message, state: FSMContext):
    kb: Keyboards = ctx_data.get()['keyboards']

    mailing_users = clear_mailing_users(message.text)

    markup = await kb.back_kb()

    try:
        write_mailing_users(mailing_users, message.from_user.id)
        await message.answer("Загружено", reply_markup=markup)
    except Exception as ex:
        await message.answer(f"Ошибка {ex}", reply_markup=markup)


async def start_manual_mailing(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.back_kb()

    user_id = callback_data["user_id"]
    client_id = callback_data["client_id"]
    command = callback_data["command"]

    clients = db.get_clients(str(user_id))

    markup = await kb.manual_mailing_kb(user_id=user_id, clients=clients)

    if not clients:
        await callback.message.answer('Сначала добавьте профиль в разделе "Добавить профиль"', reply_markup=markup)
        return

    if user_id != "" and client_id == "":
        await callback.message.answer("Выберите номер для запуска.\n Если в списке нет номеров, добавьте их в главном меню!", reply_markup=markup)
        return

    if client_id != "" and command == "":
        client = db.get_client(client_id)
        markup = await kb.back_kb()
        mes = await callback.message.answer("Запускаю рассылку по базе", reply_markup=markup)
        from pyrogram.errors.exceptions.bad_request_400 import PeerFlood
        from sqlite3 import OperationalError
        try:
            file = open(f"mailing/{callback.from_user.id}.txt")
            mailing_users = file.read().split(",")
            await mailing(client, mailing_users)
            await callback.message.answer("Разослано!", reply_markup=markup)
        except PeerFlood:
            await callback.message.answer(f"Возможно вы попали под спам фильтр.Обратитесь к @SpamBot для проверки", reply_markup=markup)
        except OperationalError:
            await callback.message.answer(f"Рассылка уже запущена.Дож", reply_markup=markup)
        except Exception as ex:
            await callback.message.answer(f"Ошибка {ex}", reply_markup=markup)

        finally:
            await mes.delete()


async def start_receive(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.back_kb()
    user_id = callback_data["user_id"]
    client_id = callback_data["client_id"]
    command = callback_data["command"]

    clients = db.get_clients(user_id)

    markup = await kb.start_receive_kb(user_id=user_id, clients=clients)

    if not clients:
        await callback.message.answer('Сначала добавьте профиль в разделе "Добавить профиль"', reply_markup=markup)
        return

    if user_id != "" and client_id == "":
        markup = await kb.start_receive_kb(user_id=user_id, clients=clients)
        await callback.message.answer("Выберите номер для запуска.\n Если в списке нет номеров, добавьте их в главном меню!", reply_markup=markup)
        return

    if client_id != "" and command == "":
        client = db.get_client(client_id)
        if not client.ai_settings:
            markup = await kb.back_kb()
            await callback.message.answer('Сначала настройте бота в разделе "Редактировать профиль"', reply_markup=markup)
            return
        try:
            user_active_clients[callback.from_user.id]
        except:
            user_active_clients[callback.from_user.id] = None
        if user_active_clients[callback.from_user.id]:
            task = user_active_clients[callback.from_user.id]
            await stop_receiving(client, task)
            await callback.message.answer("Остановил бота", reply_markup=markup)
            user_active_clients[callback.from_user.id] = None
            return
        clnt = await start_receiving(client)
        db.set_client_active
        user_active_clients[callback.from_user.id] = clnt
        markup = await kb.back_kb()
        await callback.message.answer("Запустил бота", reply_markup=markup)


async def client_collect_data(message: types.Message, state: FSMContext):

    kb: Keyboards = ctx_data.get()['keyboards']
    try:
        data = message.text.replace(" ", "").split(",")
        api_id = data[0]
        api_hash = data[1]
        phone = data[2]

        client_data[message.from_user.id] = {}
        client_data[message.from_user.id]["api_id"] = data[0]
        client_data[message.from_user.id]["api_hash"] = data[1]
        client_data[message.from_user.id]["phone"] = data[2]

        markup = await kb.client_kb("1")
        await message.answer(f"Текущие данные: \napi_id: {api_id} ,\napi_hash: {api_hash} , \nphone: {phone} \nЧтобы продолжить нажмите далее", reply_markup=markup)

    except Exception as ex:
        print(ex)
        await message.answer(f"Ошибка в обработке данных, проверьте данные и попробуйте снова.")


async def client_add_profile(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    db: Database = ctx_data.get()['db']
    kb: Keyboards = ctx_data.get()['keyboards']
    markup = await kb.back_kb()
    user = db.get_user(callback.from_user.id)
    if not user.has_access:
        await pay(callback)
        return

    if callback_data["level"] == "0":
        markup = await kb.back_kb()
        await callback.message.answer(f"""Введите api_id, api_hash и номер телефона, который вы указывали при регистрации
Формат ввода данных 12345, 12312432sdcasf123213423, +7999999999 
Через запятую в такой же постедовательности + у номера обязателен""", reply_markup=markup)
        await state.set_state("wait client data")
    elif callback_data["level"] == "1":
        data = client_data[callback.from_user.id]
        code_hash = await connect_and_get_code_hash(data)
        client_data[callback.from_user.id]["client"] = code_hash[1]
        client_data[callback.from_user.id]["code_hash"] = code_hash[0]
        await callback.message.answer(f"Отправьте код, который вам прислал телеграмм", reply_markup=markup)
        await state.set_state("connect")


async def connect_client(message: types.Message, state: FSMContext):
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    try:
        phone = client_data[message.from_user.id]["phone"]
        markup = await kb.back_kb()
        me = await connect_with_password(client_data[message.from_user.id], message.text, client_data[message.from_user.id]["client"])
        await message.answer(f"Успешно {me.first_name} {me.last_name}", reply_markup=markup)
        db.create_client(message.from_id,
                         client_data[message.from_user.id]["phone"],
                         client_data[message.from_user.id]["api_id"],
                         client_data[message.from_user.id]["api_hash"],
                         )
        os.system(f"cp sessions/{phone}.session mailing_session")
    except Exception as ex:
        markup = await kb.back_kb()
        await message.answer(f"Ошибка {ex}", reply_markup=markup)
    finally:
        client_data.pop(message.from_user.id)


async def edit_client(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    db: Database = ctx_data.get()['db']

    user = db.get_user(callback.from_user.id)
    if not user.has_access:
        await pay(callback)
        return
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    user_id = callback_data.get("user_id")
    client_id = callback_data.get("client_id")
    command = callback_data.get("command")
    telegram_id = callback.from_user.id

    data = {}

    data[telegram_id] = client_id

    await state.set_data(data)

    if user_id != "" and client_id == "":
        clients = db.get_clients(user_id)
        markup = await kb.edit_client_kb(clients=clients)
        await callback.message.answer("Выберите номер для редактирования.\n Если в списке нет номеров, добавьте их в главном меню!", reply_markup=markup)

    if client_id != "" and command == "":
        markup = await kb.edit_client_kb(client_id=client_id, user_id=user_id)
        await callback.message.answer("Выберите пункт меню", reply_markup=markup)

    if client_id != "" and command == "AI":
        text = db.get_client_ai_settings(client_id)
        markup = await kb.back_kb()
        await callback.message.answer("Введите настройки для нейросети.\n Текущие настройки: \n".format(text), reply_markup=markup)
        await state.set_state('input ai settings')
        return

    if client_id != "" and command == "text":
        text = db.get_client_mailing_text(client_id)
        markup = await kb.back_kb()
        await callback.message.answer("Введите текст для рассылки.\n Текущий текст: {}\n".format(text), reply_markup=markup)
        await state.set_state('input mailing text')
        return

    if client_id != "" and command == "stat":
        markup = await kb.back_kb()
        text = db.get_client_gs_name(client_id)
        await callback.message.answer("""Введите название Гугл таблицы, в которой будут отображаться данные.
Внимание!!! Дайте доступ к гугл таблице аккаунту "my-test-account@brave-design-383019.iam.gserviceaccount.com" иначе данные не будут отображаться
Вы можете добавлять несколько номеров в одну таблицу""", reply_markup=markup)
        await state.set_state('input gs name')
        return

    if client_id != "" and command == "info":
        data = db.get_client(client_id)
        markup = await kb.back_kb()
        text = create_text(data)
        await callback.message.answer(text, reply_markup=markup)


async def wait_ai_settings(message: types.Message, state: FSMContext):
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    data = await state.get_data()

    client_id = data[message.from_user.id]

    db.edit_client_ai_settings(message.text, client_id)
    markup = await kb.back_kb()
    await message.answer("Обновлены настройки нейросети.\nНовые настройки:\n{}".format(message.text), reply_markup=markup)


async def wait_mailing_text(message: types.Message, state: FSMContext):
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    data = await state.get_data()
    client_id = data[message.from_user.id]

    db.edit_client_mailing_text(message.text, client_id)
    markup = await kb.back_kb()

    await message.answer("Обновлен текст рассылки.\nНовые настройки:\n{}".format(message.text), reply_markup=markup)


async def wait_gs_name(message: types.Message, state: FSMContext):
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    data = await state.get_data()
    client_id = data[message.from_user.id]

    db.edit_client_gs(message.text, client_id)
    markup = await kb.back_kb()

    await message.answer("Обновлена таблица для сбора статистики.\nНовые настройки:\n{}".format(message.text), reply_markup=markup)


def register_user_handlers(dp: Dispatcher, cfg: Config, kb: Keyboards, db: Database):
    dp.register_message_handler(start, commands=["start"], state="*")
    dp.register_callback_query_handler(start, kb.back_cd.filter(), state="*")

    dp.register_message_handler(client_collect_data, state="wait client data")
    dp.register_callback_query_handler(
        client_add_profile, kb.add_profile_cd.filter(), state="*")
    dp.register_message_handler(connect_client, state="connect")

    dp.register_callback_query_handler(
        edit_client, kb.edit_client_cd.filter(), state="*")

    dp.register_callback_query_handler(
        wait_mailing_base, lambda call: call.data == "base", state="*")
    dp.register_message_handler(
        collect_mailing_base, state="wait mailing base")

    dp.register_callback_query_handler(
        start_manual_mailing, kb.manual_mailing_cd.filter(), state="*")
    dp.register_callback_query_handler(
        copy_settings, kb.copy_settings_cd.filter(), state="*")
    dp.register_callback_query_handler(
        start_receive, kb.start_receiving_cd.filter(), state="*")

    dp.register_callback_query_handler(
        help, lambda call: call.data == "help", state="*")
    dp.register_callback_query_handler(
        pay, lambda call: call.data == "pay", state="*")

    dp.register_message_handler(wait_ai_settings, state="input ai settings")
    dp.register_message_handler(wait_mailing_text, state="input mailing text")
    dp.register_message_handler(wait_gs_name, state="input gs name")
