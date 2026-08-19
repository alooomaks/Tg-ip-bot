import os

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)


# =========================
# НАСТРОЙКИ
# =========================

TOKEN = os.environ["BOT_TOKEN"]


# =========================
# /START
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = """💬 УСЛОВИЯ ДЛЯ ПОЛУЧЕНИЯ

1️⃣ Напиши 10 комментариев
• Введи в поиск TikTok: детское питаниее
• Под 10 разными видео отправь данную картинку
• Видео должны быть не старше месяца

2️⃣ Поставь лайки
• Лайкай свои и чужие комментарии с этой картинкой

3️⃣ Напиши 5 ответов
• Ответь на комментарии с картинкой
• Примеры: лучшее, согласен, бесспорно, +rep
• До 3 ответов на 1 комментарий

4️⃣ Отправь скриншоты
• Сделай скрины всех комментариев
• Нажми кнопку «Я выполнил»

⏳ Выдача: до 1 часа"""

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Я ВЫПОЛНИЛ",
                callback_data="completed"
            )
        ]
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# КНОПКА
# =========================

async def button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.data == "completed":

        await query.message.reply_text(
            "📸 Отлично!\n\n"
            "Теперь отправь сюда скриншоты "
            "выполненных заданий.\n\n"
            "⏳ После проверки результат будет "
            "выдан в течение часа."
        )


# =========================
# ПОЛУЧЕНИЕ ФОТО
# =========================

async def photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "✅ Скриншот получен.\n\n"
        "Если у тебя есть ещё скриншоты — "
        "отправь их следующим сообщением.\n\n"
        "После отправки всех скриншотов "
        "ожидай проверки."
    )


# =========================
# ОБЫЧНЫЙ ТЕКСТ
# =========================

async def text_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "ℹ️ Используй кнопку «Я ВЫПОЛНИЛ», "
        "чтобы отправить выполнение."
    )


# =========================
# ЗАПУСК
# =========================

def main():

    app = Application.builder().token(TOKEN).build()

    # /start
    app.add_handler(
        CommandHandler("start", start)
    )

    # Кнопки
    app.add_handler(
        CallbackQueryHandler(button)
    )

    # Фотографии
    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            photo
        )
    )

    # Обычные сообщения
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_message
        )
    )

    print("Бот запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()
