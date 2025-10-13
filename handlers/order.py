from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from config import ADMIN_ID
from database.db import async_session
from database.models import Order
import re
from keyboards.subcategories import sleep_kb

router = Router()

class OrderForm(StatesGroup):
    consult_waiting_for_phone = State()
    order_waiting_for_name = State()
    order_waiting_for_phone = State()
    order_waiting_for_comment = State()

@router.callback_query(F.data.startswith("ask_"))
async def ask_question(callback: CallbackQuery):
    product_id = callback.data.split("_", 1)[1]
    await callback.message.answer("💬 Пожалуйста, задайте ваш вопрос по этому товару. Наш менеджер свяжется с вами в ближайшее время.")
    
    await callback.answer()


@router.callback_query(F.data.startswith("consult_"))
async def ask_consult(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_", 1)[1]
    await state.update_data(product_id=product_id)
    await callback.message.answer("📞 Введите ваш номер телефона (в формате +79991234567):")
    await state.set_state(OrderForm.consult_waiting_for_phone)
    await callback.answer()

@router.message(OrderForm.consult_waiting_for_phone)
async def process_consult_phone(message: types.Message, state: FSMContext):
    raw = message.text.strip()
    digits = re.sub(r'\D', '', raw)
    if not (digits.startswith("7") and len(digits) == 11):
        await message.answer("❌ Неверный формат телефона. Попробуйте снова (+79991234567).")
        return
    phone = f"+{digits}"

    data = await state.get_data()
    product_id = data.get("product_id")


    await message.bot.send_message(
        ADMIN_ID,
        f"📞 <b>Заявка на консультацию</b>\n\nТелефон: {phone}\nТовар ID: {product_id}",
        parse_mode="HTML"
    )

    await message.answer("✅ Спасибо! Мы скоро свяжемся с вами.")
    await state.clear()

@router.callback_query(F.data.startswith("order_"))
async def start_order(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_", 1)[1]
    await state.update_data(product_id=product_id)
    await callback.message.answer("📝 Введите ваше имя:")
    await state.set_state(OrderForm.order_waiting_for_name)
    await callback.answer()

@router.message(OrderForm.order_waiting_for_name)
async def order_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("📞 Теперь введите ваш номер телефона (в формате +79991234567):")
    await state.set_state(OrderForm.order_waiting_for_phone)

@router.message(OrderForm.order_waiting_for_phone)
async def order_phone(message: types.Message, state: FSMContext):
    raw = message.text.strip()
    digits = re.sub(r'\D', '', raw)
    if not (digits.startswith("7") and len(digits) == 11):
        await message.answer("❌ Неверный формат телефона. Попробуйте снова (+79991234567).")
        return
    phone = f"+{digits}"
    await state.update_data(phone=phone)
    await message.answer("💬 Добавьте комментарий (опционально) или напишите «-», если без комментария:")
    await state.set_state(OrderForm.order_waiting_for_comment)

@router.message(OrderForm.order_waiting_for_comment)
async def order_comment(message: types.Message, state: FSMContext):
    comment = "" if message.text.strip() == "-" else message.text.strip()
    data = await state.get_data()

    name = data.get("name")
    phone = data.get("phone")
    product_id = data.get("product_id")


    await message.bot.send_message(
        ADMIN_ID,
        f"🛒 <b>Новый заказ</b>\n\nИмя: {name}\nТелефон: {phone}\nКомментарий: {comment}\nТовар ID: {product_id}",
        parse_mode="HTML"
    )

    try:
        async with async_session() as session:
            order = Order(name=name, phone=phone, comment=comment, product_id=product_id)
            session.add(order)
            await session.commit()
    except Exception:
        pass

    await message.answer("✅ Ваш заказ принят! Мы свяжемся с вами в ближайшее время.")
    await state.clear()

@router.message(F.data == "back_sleep_ru")
async def back_to_sleep_ru(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛏️ Спальная мебель:\nВыберите подкатегорию 👇",
        reply_markup=sleep_kb()
    )
    await callback.answer()
 