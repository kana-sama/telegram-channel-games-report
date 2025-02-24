from os import getenv
from dotenv import load_dotenv
from pyrogram import Client, types, enums

load_dotenv()
app = Client(name="playdate-games-report", api_id=getenv("API_ID"), api_hash=getenv("API_HASH"))


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

            title = message.caption.split("\n")[0].strip()
            link = message.link

            game = (title, link)

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
            return f"`- `{game[0]} [[↗]]({game[1]})\n"

        def append_title(title):
            return f"\n**{title}**\n"

        for (title, games) in [("In Progress", in_progress), ("Completed", completed), ("Todo", todo), ("Dropped", dropped), ("Scoring", scoring), ("Apps", apps)]:
            games.reverse()
            text += append_title(title)
            text += "".join([append_game(game) for game in games])

        print(len(text))

        await app.edit_message_text(
            chat_id=getenv("CHANNEL_ID"),
            message_id=int(getenv("REPORT_MESSAGE_ID")),
            text=text,
            parse_mode=enums.ParseMode.MARKDOWN
        )


app.run(main())
