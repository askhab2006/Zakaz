from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb():
    kb = [
        [InlineKeyboardButton(text="🛏️ Спальная мебель", callback_data="cat_sleep")],
        [InlineKeyboardButton(text="🛏️ Кровати", callback_data="cat_beds")],
        [InlineKeyboardButton(text="🍳 Кухонная мебель", callback_data="cat_kitchen")],
        [InlineKeyboardButton(text="🛋️ Мягкая мебель", callback_data="cat_soft")],
        [InlineKeyboardButton(text="📚 Столы и стулья", callback_data="cat_tables")],
        [InlineKeyboardButton(text="📺 Тумбы и комоды", callback_data="cat_commodes")],
        [InlineKeyboardButton(text="🛏️ Матрасы", callback_data="cat_mattresses")],
        [InlineKeyboardButton(text="🚪 Шкафы", callback_data="cat_wardrobes")],
        [InlineKeyboardButton(text="ℹ️ О компании / Контакты", callback_data="cat_about")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


