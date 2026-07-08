import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiohttp import web

API_TOKEN = '8995419824:AAG3S2y5SLZDx8fAI-8EkiBXkpQRtiaBg4s'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Маҳсулотлар базаси (Расмлар, номлар ва нархлар)
PRODUCTS = {
    'espresso': {
        'uz': '☕ Эспрессо', 'ru': '☕ Эспрессо', 'en': '☕ Espresso', 
        'price': 15000, 'image': 'https://images.unsplash.com/photo-1510972527409-cca19de31749'
    },
    'cappuccino': {
        'uz': '🥛 Капучино', 'ru': '🥛 Капучино', 'en': '🥛 Cappuccino', 
        'price': 22000, 'image': 'https://images.unsplash.com/photo-1572442388796-11668a67e13a'
    },
    'latte': {
        'uz': '🍫 Латте', 'ru': '🍫 Латте', 'en': '🍫 Latte', 
        'price': 24000, 'image': 'https://images.unsplash.com/photo-1528952686551-542043782ab9'
    }
}

# Кўп тилли матнлар луғати
TEXTS = {
    'welcome': {
        'uz': "👋 **I26 Coffee** ботига хуш кeлибсиз! Қуйидаги тугмалардан бирини танланг:",
        'ru': "👋 Добро пожаловать в бот **I26 Coffee**! Выберите одну из кнопок ниже:",
        'en': "👋 Welcome to **I26 Coffee** bot! Choose one of the buttons below:"
    },
    'menu_btn': {'uz': '☕ Меню', 'ru': '☕ Меню', 'en': '☕ Menu'},
    'loc_btn': {'uz': '📍 Манзил', 'ru': '📍 Адрес', 'en': '📍 Location'},
    'contact_btn': {'uz': '📞 Алоқа', 'ru': '📞 Контакты', 'en': '📞 Contact'},
    'lang_btn': {'uz': '🌐 Тилни ўзгартириш', 'ru': '🌐 Изменить язык', 'en': '🌐 Change Language'},
    'order_btn': {'uz': '🛒 Буюртма бeриш', 'ru': '🛒 Заказать', 'en': '🛒 Order'},
    'ask_phone': {
        'uz': '📞 Илтимос, пастки тугмани босиб тeлeфон рақамингизни юборинг:',
        'ru': '📞 Пожалуйста, отправьте свой номер телефона, нажав кнопку ниже:',
        'en': '📞 Please send your phone number by pressing the button below:'
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

# Фойдаланувчи ҳолатлари
class OrderState(StatesGroup):
    language = State()
    main_menu = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_payment = State()

def get_main_menu(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS['menu_btn'][lang])],
            [KeyboardButton(text=TEXTS['loc_btn'][lang]), KeyboardButton(text=TEXTS['contact_btn'][lang])],
            [KeyboardButton(text=TEXTS['lang_btn'][lang])]
        ],
        resize_keyboard=True
    )

def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.reply("🌐 Тилни танланг / Выберите язык / Choose language:", reply_markup=get_lang_keyboard())
    await state.set_state(OrderState.language)

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    await callback.message.delete()
    await callback.message.answer(TEXTS['welcome'][lang], reply_markup=get_main_menu(lang), parse_mode="Markdown")
    await state.set_state(OrderState.main_menu)

@dp.message(F.text.in_(['☕ Меню', '☕ Menu']))
async def show_menu(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get('lang', 'uz')
    
    for key, prod in PRODUCTS.items():
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS['order_btn'][lang], callback_data=f"buy_{key}")]
        ])
        caption = f"*{prod[lang]}*\n💰 {prod['price']:,} сўм"
        await message.answer_photo(photo=prod['image'], caption=caption, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("buy_"))
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    product_key = callback.data.split("_")[1]
    await state.update_data(product=product_key)
    user_data = await state.get_data()
    lang = user_data.get('lang', 'uz')
    
    phone_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS['send_phone_btn'][lang], request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await callback.message.answer(TEXTS['ask_phone'][lang], reply_markup=phone_kb)
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone, F.contact)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    user_data = await state.get_data()
    lang = user_data.get('lang', 'uz')
    
    await message.answer(TEXTS['ask_address'][lang], reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(OrderState.waiting_for_address)

@dp.message(OrderState.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    user_data = await state.get_data()
    lang = user_data.get('lang', 'uz')
    
    pay_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Click", callback_data="pay_click")],
        [InlineKeyboardButton(text="🔵 Payme", callback_data="pay_payme")]
    ])
    await message.answer(TEXTS['pay_choose'][lang], reply_markup=pay_kb)
    await state.set_state(OrderState.waiting_for_payment)

@dp.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: types.CallbackQuery, state: FSMContext):
    system = callback.data.split("_")[1]
    user_data = await state.get_data()
    lang = user_data.get('lang', 'uz')
    
    # Тўлов тизимлари учун ҳавола (Мисол сифатида Click/Payme асосий саҳифаси қўйилди)
    link = "https://my.click.uz/" if system == "click" else "https://payme.uz/"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 Оплатить / Тўлаш", url=link)]
    ])
    
    await callback.message.answer(f"{TEXTS['success_order'][lang]} ({system.upper()})", reply_markup=kb)
    await callback.message.answer(TEXTS['welcome'][lang], reply_markup=get_main_menu(lang), parse_mode="Markdown")
    await state.set_state(OrderState.main_menu)

@dp.message(F.text.in_(['📍 Манзил', '📍 Адрес', '📍 Location']))
async def show_location(message: types.Message, state: FSMContext):
    await message.reply("📍 Бизнинг манзил: Тошкент шаҳри, Чилонзор кўчаси, 26-уй.")
    await bot.send_location(message.chat.id, latitude=41.2825, longitude=69.2136)

@dp.message(F.text.in_(['📞 Алоқа', '📞 Контакты', '📞 Contact']))
async def show_contact(message: types.Message, state: FSMContext):
    await message.reply("📞 Боғланиш учун телефон: +998 (90) 123-45-67\n🕒 Иш вақти: 08:00 - 22:00")

@dp.message(F.text.in_(['🌐 Тилни ўзгартириш', '🌐 Изменить язык', '🌐 Change Language']))
async def change_lang(message: types.Message, state: FSMContext):
    await message.reply("🌐 Тилни танланг / Выберите язык / Choose language:", reply_markup=get_lang_keyboard())
    await state.set_state(OrderState.language)

async def handle(request):
    return web.Response(text="Бот янгиланди ва ишламоқда!")

async def main():
    asyncio.create_task(dp.start_polling(bot))
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
    await site.start()
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
