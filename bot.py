import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, catalog, order
from database.db import init_db
from handlers.admin import add_product, view_orders, manage_products
import logging


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(order.router)
    dp.include_router(add_product.router)
    dp.include_router(view_orders.router)
    dp.include_router(manage_products.router)
    
    await init_db()

    print("🤖 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
