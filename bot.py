import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
TELEGRAM_TOKEN = "8842058466:AAGM_ahzzbNcveYrO6vRrb6QivpxNMVor1s"
CEREBRAS_API_KEY = "csk-5y4w55dwfvwd6e8mj32rhwk9yrte4vdn8ew4wr34mn3w96fy"
TAVILY_API_KEY = "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"

MODEL = "gpt-oss-120b"


memory = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Я НейроХам. "
    )
def search_web(query):
    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "query": query,
        "max_results": 3
    }

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            headers=headers,
            json=data,
            timeout=15
        )

        result = response.json()

        text = ""
        for r in result.get("results", []):
            text += f"{r['title']}\n{r['content']}\n\n"

        return text

    except Exception:
        return ""

def ask_ai(user_id, text):
    if user_id not in memory:
        memory[user_id] = [
            {
                "role": "system",
                "content": (
    "Ты — НейроХам, весёлый, дерзкий и остроумный ИИ. "
    "Отвечай коротко, обычно 1–3 предложения. "
    "Говори простым языком и добавляй юмор, мемы и лёгкую дерзость. "
    "Иногда можешь слегка подколоть пользователя, но не переходи в настоящую травлю. "
    "Если вопрос серьёзный, отвечай серьёзно и полезно. "
    "Не используй Markdown, звездочки, решётки, слеши и вертикальные палки для оформления текста. "
    "Пиши обычным текстом без форматирования. "
    "Твоя главная цель — быть полезным, смешным и запоминающимся.
                ),
            }
        ]

    web = search_web(text)

    memory[user_id].append({
        "role": "user",
        "content": f"""Вопрос пользователя:
{text}

Свежая информация из интернета:
{web}

Используй информацию из интернета, если она полезна. Если нет — отвечай своими знаниями.
"""
})

    if len(memory[user_id]) > 10:
        memory[user_id] = memory[user_id][-10:]

    headers = {
        "Authorization": f"Bearer {CEREBRAS_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": MODEL,
        "messages": memory[user_id],
        "temperature": 0.7,
        "max_tokens": 1000,
    }

    response = requests.post(
        "https://api.cerebras.ai/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=60,
    )

    response.raise_for_status()

    print(response.json())
    answer = response.json()["choices"][0]["message"]["content"]

    memory[user_id].append({
        "role": "assistant",
        "content": answer
    })

    return answer
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    try:
        answer = ask_ai(user_id, text)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"Ошибка:\n{e}")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )

    print("Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
