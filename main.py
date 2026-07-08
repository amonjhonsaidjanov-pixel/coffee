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

TEXTS = {
    'welcome': {
        'uz': "👋 **I26 Coffee** ботига хуш кeлибсиз! Қуйидаги тугмалардан бирини танланг:",
        'ru': "👋 Добро пожаловать в бот **I26 Coffee**! Выберите одну из кнопок ниже:",
        'en': "👋 Welcome to **I26 Coffee** bot! Choose one of the buttons below:"
    },
    'menu_btn': {'uz': '☕ Иловани очиш (Меню)', 'ru': '☕ Открыть приложение', 'en': '☕ Open App'},
    'pay_info_btn': {'uz': '💳 Тўлов усуллари', 'ru': '💳 Способы оплаты', 'en': '💳 Payment Methods'},
    'lang_btn': {'uz': '🌐 Тилни ўзгартириш', 'ru': '🌐 Изменить язык', 'en': '🌐 Change Language'},
    'ask_phone': {
        'uz': '📞 Раҳмат! Илтимос, пастки тугмани босиб тeлeфон рақамингизни юборинг:',
        'ru': '📞 Спасибо! Пожалуйста, отправьте свой номер телефона:',
        'en': '📞 Thank you! Please send your phone number:'
    },
    'send_phone_btn': {'uz': '📱 Рақамни юбориш', 'ru': '📱 Отправить номер', 'en': '📱 Send number'},
    'ask_address': {
        'uz': '📍 Доставка учун манзилингизни матн шаклида ёзиб юборинг:',
        'ru': '📍 Отправьте адрес для доставки в виде текста:',
        'en': '📍 Please send your delivery address as text:'
    },
    'pay_choose': {
        'uz': '💳 Тўлов турини танланг:',
        'ru': '💳 Выберите способ оплаты:',
        'en': '💳 Choose payment method:'
    },
    'success_order': {
        'uz': '✅ Раҳмат! Буюртмангиз қабул қилинди. Тўлов учун пастки тугмани босинг:',
        'ru': '✅ Спасибо! Ваш заказ принят. Для оплаты нажмите кнопку ниже:',
        'en': '✅ Thank you! Your order is accepted. Click the button below to pay:'
    }
}

class OrderState(StatesGroup):
    language = State()
    main_menu = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_payment = State()

def get_main_menu(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS['menu_btn'][lang], web_app=WebAppInfo(url=WEBAPP_URL))],
            [KeyboardButton(text=TEXTS['pay_info_btn'][lang]), KeyboardButton(text=TEXTS['lang_btn'][lang])]
        ],
        resize_keyboard=True
    )

def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
