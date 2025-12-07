from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SUPPORT_USERNAME

def product_actions_kb(product_id: int):
    kb = [
        [InlineKeyboardButton(text="💬 Задать вопрос", url=f"https://t.me/{SUPPORT_USERNAME}",callback_data=f"ask_{product_id}")],
        [InlineKeyboardButton(text="📞 Заказать консультацию", callback_data=f"consult_{product_id}")],
        [InlineKeyboardButton(text="🛒 Оформить заказ", callback_data=f"order_{product_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
