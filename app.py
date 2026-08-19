import os
import uuid
import threading
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
SITE_URL = os.environ["SITE_URL"]

# Временное хранение токенов пользователей
users = {}


@app.route("/")
def home():
    token = request.args.get("token")

    if not token or token not in users:
        return """
        <h2>Ссылка недействительна</h2>
        """, 400

    telegram_id = users[token]

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Проверка IP</title>

        <style>
            body {{
                background:#111;
                color:white;
                font-family:Arial,sans-serif;
                display:flex;
                justify-content:center;
                align-items:center;
                min-height:100vh;
                margin:0;
            }}

            .box {{
                width:90%;
                max-width:420px;
                background:#222;
                padding:30px;
                border-radius:20px;
                text-align:center;
                box-sizing:border-box;
            }}

            button {{
                width:100%;
                padding:15px;
                margin-top:15px;
                border:0;
                border-radius:12px;
                font-size:16px;
                cursor:pointer;
            }}

            .agree {{
                background:#2ea043;
                color:white;
            }}

            .cancel {{
                background:#444;
                color:white;
            }}

            #result {{
                margin-top:20px;
                font-size:18px;
            }}
        </style>
    </head>

    <body>
        <div class="box">

            <h2>Проверка IP-адреса</h2>

            <p>
                Для продолжения сайт получит ваш IP-адрес.
                После подтверждения IP будет передан владельцу бота
                вместе с вашим Telegram ID.
            </p>

            <button class="agree" onclick="agree()">
                Я согласен
            </button>

            <button class="cancel" onclick="cancel()">
                Отмена
            </button>

            <div id="result"></div>

        </div>

        <script>
        async function agree() {{
            document.getElementById("result").innerText =
                "Получаем IP...";

            const response = await fetch("/agree?token={token}", {{
                method: "POST"
            }});

            const data = await response.json();

            if (data.success) {{
                document.getElementById("result").innerText =
                    "Готово. Ваш IP: " + data.ip;
            }} else {{
                document.getElementById("result").innerText =
                    "Произошла ошибка.";
            }}
        }}

        function cancel() {{
            document.getElementById("result").innerText =
                "Вы отказались.";
        }}
        </script>

    </body>
    </html>
    """


@app.route("/agree", methods=["POST"])
def agree():
    token = request.args.get("token")

    if not token or token not in users:
        return {"success": False}, 400

    telegram_id = users[token]

    # IP посетителя
    forwarded = request.headers.get("X-Forwarded-For")

    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.remote_addr

    # Отправляем информацию владельцу бота
    async def send_info():
        bot = Application.builder().token(BOT_TOKEN).build().bot

        await bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "✅ Пользователь согласился на передачу IP\n\n"
                f"Telegram ID: `{telegram_id}`\n"
                f"IP: `{ip}`"
            ),
            parse_mode="Markdown"
        )

    # Запускаем отправку
    threading.Thread(
        target=lambda: __import__("asyncio").run(send_info()),
        daemon=True
    ).start()

    return {
        "success": True,
        "ip": ip
    }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id

    token = str(uuid.uuid4())
    users[token] = telegram_id

    link = f"{SITE_URL}/?token={token}"

    keyboard = [
        [InlineKeyboardButton(
            "🌐 Открыть страницу",
            url=link
        )]
    ]

    await update.message.reply_text(
        "Привет!\n\n"
        f"Твой Telegram ID: {telegram_id}\n\n"
        "Для проверки IP открой страницу ниже. "
        "Перед передачей IP будет показано уведомление "
        "и потребуется подтверждение.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Твой Telegram ID: {update.effective_user.id}"
    )


def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("myid", myid)
    )

    application.run_polling()


if __name__ == "__main__":
    threading.Thread(
        target=run_bot,
        daemon=True
    ).start()

    port = int(os.environ.get("PORT", 8000))

    app.run(
        host="0.0.0.0",
        port=port
    )
