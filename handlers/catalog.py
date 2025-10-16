from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from keyboards.subcategories import sleep_kb, kitchen_kb, soft_kb, tables_chairs_kb, beds_kb
from keyboards.main_menu import main_menu_kb
from keyboards.product_actions import product_actions_kb
from database.db import async_session
from database.models import Product, ProductPhoto

router = Router()



@router.callback_query(F.data == "cat_sleep")
async def show_sleep_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛏️ Спальная мебель:\nВыберите подкатегорию 👇",
        reply_markup=sleep_kb()
    )

@router.callback_query(F.data == "cat_beds")
async def show_beds_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛏️ Кровати:\nВыберите подкатегорию 👇",
        reply_markup=beds_kb()
    )

@router.callback_query(F.data == "cat_kitchen")
async def show_kitchen_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🍳 Кухонная мебель:",
        reply_markup=kitchen_kb()
    )

@router.callback_query(F.data == "cat_soft")
async def show_soft_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛋️ Мягкая мебель:",
        reply_markup=soft_kb()
    )

@router.callback_query(F.data == "cat_tables")
async def show_tables_chairs(callback: CallbackQuery):
    await callback.message.edit_text(
        "🍽️ Столы и стулья:\nВыберите подкатегорию 👇",
        reply_markup=tables_chairs_kb()
    )

@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    try:
        if callback.message.text:
            await callback.message.edit_text(
                "🏠 Главное меню:",
                reply_markup=main_menu_kb()
            )
        else:
            await callback.message.delete()
            await callback.message.answer(
                "🏠 Главное меню:",
                reply_markup=main_menu_kb()
            )
    except Exception as e:
        await callback.message.answer(
            "🏠 Главное меню:",
            reply_markup=main_menu_kb()
        )
        print(f"⚠️ Ошибка при возврате в главное меню: {e}")

    await callback.answer()
@router.callback_query(F.data == "cat_about")
async def show_about(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ О компании / Контакты<\n\n"
        "Мы специализируемся на продаже качественной мебели из России и Турции. "
        "Наш ассортимент включает спальную мебель, кровати, кухонную мебель, мягкую мебель, "
        "столы и стулья, тумбы и комоды, матрасы и шкафы.\n\n"
        "📞 Контакты:\n"
        "Телефон: +7 (999) 123-45-67\n"
        "Email:",
        reply_markup=main_menu_kb())
    await callback.answer()


CATEGORY_MAP = {
    "sleep_ru": ("Спальная мебель", "Россия"),
    "sleep_tr": ("Спальная мебель", "Турция"),
    "beds_ru": ("Кровати", "Россия"),
    "beds_tr": ("Кровати", "Турция"),
    "kitchen_straight": ("Кухонная мебель", "Прямая"),
    "kitchen_corner": ("Кухонная мебель", "Угловая"),
    "soft_ru": ("Мягкая мебель", "Россия"),
    "soft_tr": ("Мягкая мебель", "Турция"),
    "tables_chairs_ru": ("Столы и стулья", "Россия"),
    "tables_chairs_tr": ("Столы и стулья", "Турция"),
    "cat_wardrobes": ("Шкафы", "Все"),
    "cat_mattresses": ("Матрасы", "Все"),
    "cat_commodes": ("Тумбы и комоды", "Все"),
}



@router.callback_query(F.data.in_(CATEGORY_MAP.keys()))
async def show_products_handler(callback: CallbackQuery):
    category, subcategory = CATEGORY_MAP[callback.data]

    async with async_session() as session:

        result = await session.execute(
            Product.__table__.select().where(
                Product.category.ilike(f"%{category}%")
            )
        )
        products = [row._mapping for row in result.fetchall()]

    if not products:
        await callback.message.edit_text(
            "📭 <b>К сожалению, по данной категории пока нет добавленной мебели.</b>\n\n"
            "Но не переживайте! Наш ассортимент постоянно пополняется новыми моделями.\n"
            "Рекомендуем периодически возвращаться и смотреть обновления 😊",
            parse_mode="HTML",
        )
        await callback.answer()
        return


    product = products[0]

    async with async_session() as session:
        photos_result = await session.execute(
            ProductPhoto.__table__.select().where(ProductPhoto.product_id == product["id"])
        )
        photos = [p._mapping["file_id"] for p in photos_result.fetchall()]

    caption = (
        f"<b>{product['name']}</b>\n\n"
        f"{product['description']}\n\n"
        f"🌍 {product['country']}\n"
        f"📏 {product['size']}\n"
        f"💰 {product['price']} ₽"
    )

    kb = product_actions_kb(product["id"])

    if photos:
        media = InputMediaPhoto(media=photos[0], caption=caption, parse_mode="HTML")
        await callback.message.edit_media(media=media, reply_markup=kb)
    else:
        await callback.message.edit_text(caption, parse_mode="HTML", reply_markup=kb)

    await callback.answer()