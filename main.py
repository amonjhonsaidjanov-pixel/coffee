import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

API_TOKEN = '8995419824:AAG3S2y5SLZDx8fAI-8EkiBXkpQRtiaBg4s'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="☕ Меню")],
        [KeyboardButton(text="📍 Манзил"), KeyboardButton(text="📞 Алоқа")]
    ],
    resize_keyboard=True
)

coffee_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="☕ Эспрессо - 15,000 сўм", callback_data="order_espresso")],
        [InlineKeyboardButton(text="🥛 Капучино - 22,000 сўм", callback_data="order_cappuccino")],
        [InlineKeyboardButton(text="🍫 Латте - 24,000 сўм", callback_data="order_latte")]
    ]
)

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply(f"👋 Ассалому алайкум, {message.from_user.first_name}!\n**I26 Coffee** ботига хуш келибсиз.", reply_markup=main_menu, parse_mode="Markdown")

@dp.message(lambda message: message.text == "☕ Меню")
async def show_menu(message: types.Message):
    await message.reply("Ичимликларни танланг:", reply_markup=coffee_menu)

@dp.message(lambda message: message.text == "📍 Манзил")
async def show_location(message: types.Message):
    await message.reply("📍 Бизнинг манзил: Тошкент шаҳри, Чилонзор кўчаси, 26-уй.")
    await bot.send_location(message.chat.id, latitude=41.2825, longitude=69.2136)

@dp.message(lambda message: message.text == "📞 Алоқа")
async def show_contact(message: types.Message):
    await message.reply("📞 Боғланиш учун телефон: +998 (90) 123-45-67\n🕒 Иш вақти: 08:00 - 22:00")

async def handle(request):
    return web.Response(text="Бот ишлаяпти!")

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
