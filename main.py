import asyncio
import logging
import os
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
)
from aiohttp import web

API_TOKEN = '8995419824:AAG3S2y5SLZDx8fAI-8EkiBXkpQRtiaBg4s'
WEBAPP_URL = 'https://coffee-4i66.onrender.com' 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class OrderState(StatesGroup):
    language = State()
    main_menu = State()
    waiting_for_phone = State()
    waiting_for_address = State()

# Асосий меню
def get_main_menu(lang):
    kb = [
        [KeyboardButton(text='☕ Менюни очиш', web_app=WebAppInfo(url=WEBAPP_URL))],
        [KeyboardButton(text='💳 Тўлов усуллари'), KeyboardButton(text='🌐 Тил')]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Тилни танланг:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")]
    ]))
    await state.set_state(OrderState.language)

@dp.callback_query(F.data == "lang_uz")
async def set_lang(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("👋 I26 Coffee га хуш келибсиз!", reply_markup=get_main_menu('uz'))
    await state.set_state(OrderState.main_menu)

# Иловадан маълумот олиш
@dp.message(F.web_app_data)
async def web_app_data(message: types.Message, state: FSMContext):
    data = json.loads(message.web_app_data.data)
    await state.update_data(total_price=data['total_price'])
    
    # 📱 Рақам сўраш тугмаси
    phone_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Рақамни улашиш", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer(f"💰 Сумма: {data['total_price']} сўм. Телефон рақамингизни юборинг:", reply_markup=phone_kb)
    await state.set_state(OrderState.waiting_for_phone)

# Рақамни қабул қилиш
@dp.message(OrderState.waiting_for_phone, F.contact)
async def get_phone(message: types.Message, state: FSMContext):
    # 📍 Локация сўраш тугмаси
    loc_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Локацияни юбориш", request_location=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("✅ Рақам қабул қилинди. Илтимос, манзилингиз учун локацияни юборинг:", reply_markup=loc_kb)
    await state.set_state(OrderState.waiting_for_address)

# Локацияни қабул қилиш
@dp.message(OrderState.waiting_for_address, F.location)
async def get_location(message: types.Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Click (Иловада очиш)", web_app=WebAppInfo(url="https://my.click.uz/"))],
        [InlineKeyboardButton(text="🔵 Payme (Иловада очиш)", web_app=WebAppInfo(url="https://payme.uz/"))]
    ])
    await message.answer("✅ Манзил қабул қилинди. Тўловни танланг:", reply_markup=kb)

# Веб сервер қисми
async def handle(request):
    try:
        return web.Response(text=open('index.html', 'r', encoding='utf-8').read(), content_type='text/html')
    except:
        return web.Response(text="Бот ишламоқда!")

async def main():
    asyncio.create_task(dp.start_polling(bot))
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
    await site.start()
    while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
