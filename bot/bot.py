import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.filters import StateFilter
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.types.input_file import FSInputFile
from aiogram import F
import re
import datetime

import os

from bot.botBack import *
from parser.rasin import dbINIT, cleardb, rmExelOFO
from parser.rasinZO import dbINIT_ZO, rmExelOZFO
import bot.old_selecter as oldSel

i_chek = '✓'

admins = [...]

logging.basicConfig(level=logging.INFO)

bot = Bot(token="...")

dp = Dispatcher()


#print(glb_commands)

@dp.message(Command("start"))
async def bot_cmd_start(message: types.Message):
    user_INIT(message)
    await message.answer(f"Здраствуйте {f",{message.from_user.first_name}" if message.from_user.first_name else ''} {message.from_user.last_name if message.from_user.last_name else ''} \U0001F44B.\nС помощью данного бота вы можете получать любую информацию по расписанию\nПросто пишите что хотите увидеть!")

#region settings

def make_settings_buttons(message):
    sets = usr_get_settings(message)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=f"Абривиатуры дисциплин {i_chek if sets[0] else ''}", callback_data='schg_abr'))
    builder.add(types.InlineKeyboardButton(text=f"Упрощение групп {i_chek if sets[1] else ''}", callback_data='schg_grp'))
    builder.add(types.InlineKeyboardButton(text=f"Обрезка инициалов {i_chek if sets[2] else ''}", callback_data='schg_inc'))
    builder.add(types.InlineKeyboardButton(text=f"Линии между парами {i_chek if sets[3] else ''}", callback_data='schg_line'))
    builder.add(types.InlineKeyboardButton(text=f"Отображение перподавателя {i_chek if sets[4] else ''}", callback_data='schg_sPrp'))
    builder.add(types.InlineKeyboardButton(text=f"Отображение типа {i_chek if sets[5] else ''}", callback_data='schg_sTyp'))
    builder.add(types.InlineKeyboardButton(text=f"Отображение группы {i_chek if sets[6] else ''}", callback_data='schg_sGrp'))
    builder.add(types.InlineKeyboardButton(text=f"Отображение даты {i_chek if sets[7] else ''}", callback_data='schg_sDat'))
    builder.add(types.InlineKeyboardButton(text='закрыть', callback_data='msg_remove'))
    builder.adjust(1)
    return builder.as_markup()

@dp.message(Command("settings"))
async def bot_cmd_settings(message: types.Message):
    user_INIT(message)
    buttons = make_settings_buttons(message)
    await message.answer('Настройки', reply_markup=buttons)

@dp.callback_query(F.data.startswith("schg_"))
async def bot_chg_sets(callback: types.CallbackQuery):
    chg = callback.data.split('_')[1]
    usr_chg_settings(callback.message, chg)
    buttons = make_settings_buttons(callback.message)
    await callback.message.edit_reply_markup(reply_markup=buttons)

#endregion


#region weeks

def make_week_buttons(message):
    weeks = weeks_get()
    usr_week = usr_get_week(message)
    builder = InlineKeyboardBuilder()
    for week in weeks:
        if week == usr_week:
            builder.add(types.InlineKeyboardButton(text=f"Неделя {week} {i_chek}", callback_data=f"chgweek_{week}"))
        else:
            builder.add(types.InlineKeyboardButton(text=f"Неделя {week}", callback_data=f"chgweek_{week}"))
    builder.add(types.InlineKeyboardButton(text='закрыть', callback_data='msg_remove'))
    builder.adjust(1)
    return builder.as_markup()

@dp.message(Command("week"))
async def bot_cmd_week(message: types.Message):
    user_INIT(message)
    buttons = make_week_buttons(message)
    await message.answer('Выберите неделю', reply_markup=buttons)

@dp.callback_query(F.data.startswith("chgweek_"))
async def bot_chg_sets(callback: types.CallbackQuery):
    week = callback.data.split('_')[1]
    usr_chg_week(callback.message, week)
    buttons = make_week_buttons(callback.message)
    await callback.message.edit_reply_markup(reply_markup=buttons)

@dp.message(Command("weeknow"))
async def bot_cmd_settings(message: types.Message):
    user_INIT(message)
    usr_chg_week(message, get_week_by_date(datetime.datetime.now().strftime(r'%d.%m')))

#endregion



@dp.message(Command("getreg"))
async def bot_cmd_settings(message: types.Message):
    user_INIT(message)


# @dp.message(Command("clear") )
# async def clear(message: types.Message):
#     cleardb()


#region import

class Importing(StatesGroup):
    adding_files = State()
    seting_week = State()
    confirm = State()

@dp.message(StateFilter(None), (F.text == '/input') & (F.from_user.id.in_(admins)))
async def bot_admin_document(message: types.Message, state: FSMContext):
    user_INIT(message)
    await state.set_state(Importing.adding_files)
    await message.answer('открыта загрузка файлов. Когда закончите жмите /done')

@dp.message(Importing.adding_files, F.document)
async def bot_admin_adding_files(message: types.Message, state: FSMContext):
    await bot.download(message.document,f"ras/{message.document.file_name}")
    #if message.document.file_name in os.listdir('ras'): await message.reply(f'{message.document.file_name} - Файл загружен')

@dp.message(Importing.adding_files, F.text == '/done')
async def bot_admin_adding_files_done(message: types.Message, state: FSMContext):
    await state.set_state(Importing.seting_week)
    await message.answer('Неделя:')

@dp.message(Importing.seting_week, F.text)
async def bot_admin_seting_week(message: types.Message, state: FSMContext):
    try: 
        int(message.text)
        await state.set_state(Importing.confirm)
        s=''
        for a in os.listdir('ras'): s += a+'\n'
        await state.update_data(week=message.text)
        await message.answer(f"Загруженые файлы:\n{s}\n{len(os.listdir('ras'))}\nНеделя: {message.text}\n\n/confirm   /decline")
    except: 
        await message.answer('не корректно')


@dp.message(Importing.confirm, F.text == '/decline')
async def bot_admin_document_decline(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Отменено")

@dp.message(Importing.confirm, F.text == '/confirm')
async def bot_admin_document_confirm(message: types.Message, state: FSMContext):
    await message.answer(f"Начинается загрузка базы данных")
    data = await state.get_data()
    await state.clear()
    # try:
    dbINIT(data['week'])
    # except Exception as e:
    #     await message.answer(f"Ошибка загрузки базы данных\n {e}")
    #     rmExelOFO()

    for file in os.listdir('logs'):
        try:
            await message.answer_document(FSInputFile(f"logs/{file}"))
            os.remove(f"logs/{file}")
        except: pass
    await message.answer('Готово!')
    vars_INIT()

#endregion


#region importZO

class ImportingZO(StatesGroup):
    adding_files = State()
    confirm = State()

@dp.message(StateFilter(None), (F.text == '/inputZO') & (F.from_user.id.in_(admins)))
async def bot_admin_document(message: types.Message, state: FSMContext):
    user_INIT(message)
    await state.set_state(ImportingZO.adding_files)
    await message.answer('открыта загрузка файлов ЗО\ОЗО. Когда закончите жмите /done')

@dp.message(ImportingZO.adding_files, F.document)
async def bot_admin_adding_files(message: types.Message, state: FSMContext):
    await bot.download(message.document,f"ras2/{message.document.file_name}")
    #if message.document.file_name in os.listdir('ras'): await message.reply(f'{message.document.file_name} - Файл загружен')

@dp.message(ImportingZO.adding_files, F.text == '/done')
async def bot_admin_adding_files_done(message: types.Message, state: FSMContext):
    await state.set_state(ImportingZO.confirm)
    s=''
    for a in os.listdir('ras2'): s += a+'\n'
    await state.update_data(week=message.text)
    await message.answer(f"Загруженые файлы:\n{s}\n{len(os.listdir('ras2'))}\n\n/confirm   /decline")

@dp.message(ImportingZO.confirm, F.text == '/decline')
async def bot_admin_document_decline(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Отменено")

@dp.message(ImportingZO.confirm, F.text == '/confirm')
async def bot_admin_document_confirm(message: types.Message, state: FSMContext):
    await message.answer(f"Начинается загрузка базы данных")
    await state.clear()
    # try:
    dbINIT_ZO()
    # except Exception as e:
    #     await message.answer(f"Ошибка загрузки базы данных\n {e}")
    # rmExelOZFO()

    for file in os.listdir('logs'):
        try:
            await message.answer_document(FSInputFile(f"logs/{file}"))
            os.remove(f"logs/{file}")
        except: pass
    await message.answer('Готово!')
    vars_INIT()

#endregion




@dp.message((F.text == '!admin') & (F.from_user.id.in_(admins)))
async def bot_admin(message: types.Message):
    user_INIT(message)


@dp.message(F.text.lower().startswith('рег')|F.text.lower().startswith('регистрация')|F.text.lower().startswith('зарегистрировать'))
async def bot_cmd_reg(message: types.Message):
    user_INIT(message)
    await message.answer(register_cmd(message))



@dp.message(F.text)
async def bot_select(message: types.Message):
    user_INIT(message)
    try:
        await message.answer(oldSel.fixSelect(oldSel.select(message.text,usr_get_week(message)),message),parse_mode=ParseMode.HTML)
    except:
        try:
            for m in oldSel.fixSelect(oldSel.select(message),message, True):
                await message.answer(m,parse_mode=ParseMode.HTML)
        except :
            await message.answer("Произошла ошибка")





@dp.callback_query(F.data == "msg_remove")
async def bot_chg_sets(callback: types.CallbackQuery):
    await callback.message.delete()

async def main():
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())