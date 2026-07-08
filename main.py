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

# ⚠️ Агар токенни ўзгартирган бўлсангиз, бу ерга ўзингизникини ёзинг
API_TOKEN = '8995419824:AAG3S2y5SLZDx8fAI-8EkiBXkpQRtiaBg4s'
WEBAPP_URL = 'https://coffee-4i66.onrender.com' 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Текстлар
TEXTS = {
    'welcome': {'uz': "👋 I26 Coffee га хуш келибсиз!", 'ru': "👋 Добро пожаловать в I26 Coffee!"},
    'menu_btn': {'uz': '☕ Менюни очиш', 'ru': '☕ Открыть меню'},
    'pay_info_btn': {'uz': '💳 Тўлов усуллари', 'ru': '💳 Способы оплаты'},
    'lang_btn': {'uz': '🌐 Тил', 'ru': '🌐 Язык'},
    'ask_phone': {'uz': '📱 Рақамингизни юборинг:', 'ru': '📱 Отправьте ваш номер:'},
    'ask_address': {'uz': '📍 Манзилни ёзинг:', 'ru': '📍 Введите адрес:'},
    'pay_choose': {'uz': '💳 Тўловни танланг:', 'ru': '💳 Выберите оплату:'}
}

class OrderState(StatesGroup):
    language = State()
    main_menu = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_payment = State()

def get_main_menu(lang):
    kb = [
        [KeyboardButton(text=TEXTS['menu_btn'][lang], web_app=WebAppInfo(url=WEBAPP_URL))],
        [KeyboardButton(text=TEXTS['pay_info_btn'][lang]), KeyboardButton(text=TEXTS['lang_btn'][lang])]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Тилни танланг / Выберите язык:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ]))
    await state.set_state(OrderState.language)

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    await callback.message.answer(TEXTS['welcome'][lang], reply_markup=get_main_menu(lang))
    await state.set_state(OrderState.main_menu)

@dp.message(F.web_app_data)
async def web_app_data(message: types.Message, state: FSMContext):
    data = json.loads(message.web_app_data.data)
    await state.update_data(total_price=data['total_price'])
    lang = (await state.get_data()).get('lang', 'uz')
    await message.answer(f"💰 Сумма: {data['total_price']} сўм. Телефон рақамингизни юборинг:", 
                         reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📱 Юбориш", request_contact=True)]], resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone, F.contact)
async def get_phone(message: types.Message, state: FSMContext):
    await message.answer("📍 Энди манзилни ёзинг:")
    await state.set_state(OrderState.waiting_for_address)

@dp.message(OrderState.waiting_for_address)
async def get_address(message: types.Message, state: FSMContext):
    total = (await state.get_data())['total_price']
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Click", web_app=WebAppInfo(url="https://my.click.uz/"))],
        [InlineKeyboardButton(text="🔵 Payme", web_app=WebAppInfo(url="https://payme.uz/"))]
    ])
    await message.answer(f"✅ Манзил қабул қилинди. Тўловни амалга оширинг:", reply_markup=kb)

# Веб сервер қисми
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
