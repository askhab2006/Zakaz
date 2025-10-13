from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
from database.db import async_session
from database.models import Order, Product

router = Router()



@router.message(F.text == "/orders")
async def view_orders(message: types.Message):
    
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ У вас нет доступа.")
    
    
    async with async_session() as session:
        result = await session.execute(Order.__table__.select())
        orders = result.fetchall()

    
    if not orders:
        await message.answer("📭 Пока нет заявок от клиентов.")
        return

    
    async with async_session() as session:
        for row in orders:
            o = row._mapping

            
            product_result = await session.execute(
                Product.__table__.select().where(Product.id == o["product_id"])
            )
            product = product_result.fetchone()
            product_name = product._mapping["name"] if product else "Не найден"

            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🕓 Новая", callback_data=f"status_new_{o['id']}"),
                    InlineKeyboardButton(text="⚙️ В работе", callback_data=f"status_work_{o['id']}"),
                    InlineKeyboardButton(text="✅ Закрыта", callback_data=f"status_done_{o['id']}")
                ]
            ])

            
            text = (
                f"🧾 <b>Заказ #{o['id']}</b>\n"
                f"👤 Имя: {o['name']}\n"
                f"📞 Телефон: {o['phone']}\n"
                f"📦 Товар: <b>{product_name}</b>\n"
                f"💬 Комментарий: {o['comment'] or '—'}\n"
                f"📌 Статус: <b>{o['status']}</b>"
            )

            await message.answer(text, parse_mode="HTML", reply_markup=kb)



@router.callback_query(F.data.startswith("status_"))
async def change_status(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    new_status = {"new": "новая", "work": "в работе", "done": "закрыта"}[parts[1]]
    order_id = int(parts[2])

    
    async with async_session() as session:
        await session.execute(
            Order.__table__.update()
            .where(Order.id == order_id)
            .values(status=new_status)
        )
        await session.commit()

    await callback.message.answer(f"✅ Статус заказа #{order_id} изменён на: {new_status}")
    await callback.answer()
