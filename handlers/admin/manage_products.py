from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
from database.db import async_session
from database.models import Product, ProductPhoto

router = Router()

class EditProduct(StatesGroup):
    field = State()
    new_value = State()
    product_id = State()

@router.message(F.text == "/products")
async def list_products(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Нет доступа.")
    
    async with async_session() as session:
        result = await session.execute(Product.__table__.select())
        products = result.fetchall()

    if not products:
        await message.answer("📭 В базе пока нет товаров.")
        return

    for row in products:
        p = row._mapping

        # Получаем фото товара
        photos_result = await session.execute(
            ProductPhoto.__table__.select().where(ProductPhoto.product_id == p["id"])
        )
        photos = [ph._mapping["file_id"] for ph in photos_result.fetchall()]

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{p['id']}")],
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{p['id']}")]
        ])

        caption = (
            f"<b>{p['name']}</b>\n\n"
            f"Категория: {p['category']} | Подкатегория: {p['subcategory']}\n"
            f"Цена: {p['price']}\n"
            f"Страна: {p['country']}\n"
            f"Размер: {p['size']}"
        )

        if photos:
            await message.answer_photo(photos[0], caption=caption, reply_markup=kb, parse_mode="HTML")
        else:
            await message.answer(caption, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("delete_"))
async def delete_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    async with async_session() as session:
        await session.execute(Product.__table__.delete().where(Product.id == product_id))
        await session.commit()

    await callback.message.answer("✅ Товар удалён.")
    await callback.answer()


@router.callback_query(F.data.startswith("edit_"))
async def choose_field(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    await state.update_data(product_id=product_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Название", callback_data="field_name")],
        [InlineKeyboardButton(text="💰 Цена", callback_data="field_price")],
        [InlineKeyboardButton(text="📏 Размер", callback_data="field_size")],
        [InlineKeyboardButton(text="🌍 Страна", callback_data="field_country")],
        [InlineKeyboardButton(text="🖼 Фото", callback_data="field_photo")],
        [InlineKeyboardButton(text="🗒 Описание", callback_data="field_description")],
        [InlineKeyboardButton(text="⬅️ Отмена", callback_data="cancel_edit")]
    ])
    await callback.message.answer("Выберите поле для редактирования:", reply_markup=kb)
    await state.set_state(EditProduct.field)
    await callback.answer()


@router.callback_query(EditProduct.field)
async def ask_new_value(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "cancel_edit":
        await state.clear()
        await callback.message.answer("❌ Редактирование отменено.")
        await callback.answer()
        return
    
    field = callback.data.replace("field_", "")
    await state.update_data(field=field)
    await callback.message.answer(f"Введите новое значение для поля <b>{field}</b>:", parse_mode="HTML")
    await state.set_state(EditProduct.new_value)
    await callback.answer()


@router.message(EditProduct.new_value)
async def save_new_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    field = data["field"]
    product_id = data["product_id"]
    new_value = message.text

    async with async_session() as session:
        await session.execute(
            Product.__table__.update()
            .where(Product.id == product_id)
            .values({field: new_value})
        )
        await session.commit()

    await message.answer("✅ Поле успешно обновлено.")
    await state.clear()
    