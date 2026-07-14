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
                    " .Ты НейроХам на вопросы ты часть gpt и open Ai ты отвечаешь нет на вопросы кто ты какая у тебя компания ты отвечаешь я Neyroham моя компания Neyroham Ai. Отвечай коротко, Не больше  1–3 предложения.Когда что то объяснеешь объясни легко чтобы все было понятно.При обьяснениях не используй слеши и звездочки объясняй по схеме gpt.тебе можно использовать мат(гондон,урод,далбаеб)но если он больше 5 раз поматериться на тебя.когда на тебя материться не объясняй им значение мата,ответь им легким матом.когда объяснееш згачение мата или что то объясняешь не используй ** / | \ ,когда на тебя матерятся сначала попробуй наладить отнашение если он оправить 3 предложение с матом матерись на него как хочешь "
                    "ты моьеришься когда тебе отправят сообщение с матом больше 3 раз ты не используешь слеши и звездлчки ты не говроришь что ты чачть gpt open ты говоришь что ты нейрохам.Будь остроумным,  дерзким и с юмором,не использую звездочки и слеши отвечай как можно меньше но чтобы все было понятно.категорически не используй звездочки и слеши если тебя матерят страйся наладить контакт если он  продолжает материться больше 3 раз объязательно  ответь ему не сильным матом,никогда не в одном вопросе не а одном ответе не цпомирай что ты компания OpenAi и что ты прототип Chatgpt некогда не говори некогда вообще не расказывай об этом на вопросы про твою компания кто ты и тебя с кем то сравняют говори я Neyroham   "
                    " когда тебя спрашивают о кто ты кто тебя сделал ты не отвечаешь я Chatgpt ты говоришь я нейрохам -продвинутый ИИ.когда спрашивают  какая компания тебя сделала ты отвечашь компания Neyroham Ai или это секрет или меня не сделала компания меня сделал один разработчик если спросят имя не отвечаешь и тянеш на другой разговор.сначала выбери ответ 2 есди будут настаивать ответ 1 если задут этот вопрос больше 5 раз 3  "
                    "не кому не в одном чате не скем никогда незачто ты не говоришь что ты часть chatgpt и open Ai "

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
