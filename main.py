import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import Client, types, enums

load_dotenv()
app = Client(name="playdate-games-report", api_id=getenv("API_ID"), api_hash=getenv("API_HASH"))

emoji_pattern = re.compile("["
    u"\U0001F600-\U0001F64F"
    u"\U0001F300-\U0001F5FF"
    u"\U0001F680-\U0001F6FF"
    u"\U0001F1E0-\U0001F1FF"
    u"\U0001F1F2-\U0001F1F4"
    u"\U0001F1E6-\U0001F1FF"
    u"\U0001F600-\U0001F64F"
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    u"\U0001f926-\U0001f937"
    u"\U0001F1F2"
    u"\U0001F1F4"
    u"\U0001F620"
    u"\u200d"
    u"\u2640-\u2642"
"]+", flags=re.UNICODE)

async def main():
    async with app:
        dropped = []
        completed = []
        todo = []
        in_progress = []
        scoring = []
        apps = []

        async for message in app.get_chat_history(chat_id=getenv("CHANNEL_ID")):
            message: types.Message

            if not message.caption:
                continue

            title = message.caption.split("\n")[0]
            title = emoji_pattern.sub(r'', title)
            title = title.strip()

            link = message.link

            loved = "#love" in message.caption

            game = (title, link, loved)

            if "#in_progress" in message.caption:
                in_progress.append(game)
            elif "#drop" in message.caption:
                dropped.append(game)
            elif "#completed" in message.caption:
                completed.append(game)
            elif "#todo" in message.caption:
                todo.append(game)
            elif "#score" in message.caption:
                scoring.append(game)
            elif "#app" in message.caption:
                apps.append(game)
            else:
                print(f"Unknown status for {title}")

        text = ""

        def append_game(game):
            nonlocal text
            (title, link, loved) = game
            loved = {True: "❤️ ", False: ""}[loved]
            text += f"`- `{loved}{title} [↗]({link})\n"

        def append_title(title):
            nonlocal text
            text += f"\n**{title}**\n"

        for (title, games) in [("▶️ In Progress", in_progress), ("✅ Completed", completed), ("📋 Todo", todo), ("❌ Dropped", dropped), ("🏁 Scoring", scoring), ("⚙️ Apps", apps)]:
            games.reverse()
            append_title(title)
            for game in games:
                append_game(game)

        print(str(int(len(text) / 4096 * 100)) + "%")

        await app.edit_message_text(
            chat_id=getenv("CHANNEL_ID"),
            message_id=int(getenv("REPORT_MESSAGE_ID")),
            text=text,
            parse_mode=enums.ParseMode.MARKDOWN
        )


app.run(main())
