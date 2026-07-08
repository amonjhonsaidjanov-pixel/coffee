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

# Тилларга кўра текстлар
TEXTS = {
    'welcome': {'uz': "👋 I26 Coffee га хуш келибсиз!", 'ru': "👋 Добро пожаловать в I26 Coffee!", 'en': "👋 Welcome to I26 Coffee!"},
    'menu': {'uz': '☕ Менюни очиш', 'ru': '☕ Открыть меню', 'en': '☕ Open Menu'},
    'pay': {'uz': '💳 Тўлов усуллари', 'ru': '💳 Способы оплаты', 'en': '💳 Payment Methods'},
    'lang': {'uz': '🌐 Тилни ўзгартириш', 'ru': '🌐 Изменить язык', 'en': '🌐 Change Language'}
}

class OrderState(StatesGroup):
    main_menu = State()

def get_main_menu(lang):
    kb = [
        [KeyboardButton(text=TEXTS['menu'][lang], web_app=WebAppInfo(url=WEBAPP_URL))],
        [KeyboardButton(text=TEXTS['pay'][lang]), KeyboardButton(text=TEXTS['lang'][lang])]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("🌐 Тилни танланг / Выберите язык / Select language:", reply_markup=get_lang_keyboard())

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    await callback.message.answer(TEXTS['welcome'][lang], reply_markup=get_main_menu(lang))
    await state.set_state(OrderState.main_menu)

@dp.message(F.text.in_(['🌐 Тилни ўзгартириш', '🌐 Изменить язык', '🌐 Change Language']))
async def change_lang(message: types.Message, state: FSMContext):
    await message.answer("🌐 Тилни танланг / Выберите язык / Select language:", reply_markup=get_lang_keyboard())

# --- Қолган қисми (Иловадан маълумот олиш, рақам ва локация) аввалгидек ---
@dp.message(F.web_app_data)
async def web_app_data(message: types.Message, state: FSMContext):
    data = json.loads(message.web_app_data.data)
    lang = (await state.get_data()).get('lang', 'uz')
    await message.answer(f"💰 Сумма: {data['total_price']} сўм. Телефон рақамингизни юборинг:", 
                         reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📱 Рақамни улашиш", request_contact=True)]], resize_keyboard=True))

@dp.message(F.contact)
async def get_phone(message: types.Message, state: FSMContext):
    await message.answer("📍 Локацияни юборинг:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📍 Локацияни юбориш", request_location=True)]], resize_keyboard=True))

@dp.message(F.location)
async def get_loc(message: types.Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Click", web_app=WebAppInfo(url="https://my.click.uz/")),
         InlineKeyboardButton(text="🔵 Payme", web_app=WebAppInfo(url="https://payme.uz/"))]
    ])
    await message.answer("✅ Манзил қабул қилинди. Тўловни танланг:", reply_markup=kb)

async def handle(request):
    return web.Response(text=open('index.html', 'r', encoding='utf-8').read(), content_type='text/html')

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
