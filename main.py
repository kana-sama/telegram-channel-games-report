import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import Client, types, enums, errors

load_dotenv()
app = Client(name="playdate-games-report", api_id=getenv("API_ID"), api_hash=getenv("API_HASH"))


IN_PROGRESS = "▶️"
TODO = "📋"
COMPLETED = "✅"
DROPPED = "❌"
SCORING = "🏁"
APP = "⚙️"
LOVED = "♥️"

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
        games = {
            IN_PROGRESS: [],
            TODO: [],
            COMPLETED: [],
            DROPPED: [],
            SCORING: [],
            APP: [],
        }

        async for message in app.get_chat_history(chat_id=getenv("CHANNEL_ID")):
            message: types.Message

            if not message.caption:
                continue

            original_title = message.caption.split("\n")[0].strip()
            rest = message.caption.split("\n")[1:]

            prefix = []

            title = emoji_pattern.sub(r'', original_title)
            title = title.strip()

            link = message.link

            loved = "#love" in message.caption

            game = (title, link, loved)

            if "#in_progress" in message.caption:
                prefix += [IN_PROGRESS]
                games[IN_PROGRESS].append(game)
            elif "#drop" in message.caption:
                prefix += [DROPPED]
                games[DROPPED].append(game)
            elif "#completed" in message.caption:
                prefix += [COMPLETED]
                games[COMPLETED].append(game)
            elif "#todo" in message.caption:
                prefix += [TODO]
                games[TODO].append(game)
            elif "#score" in message.caption:
                prefix += [SCORING]
                games[SCORING].append(game)
            elif "#app" in message.caption:
                prefix += [APP]
                games[APP].append(game)
            else:
                print(f"Unknown status for {title}")
                exit(1)

            if loved:
                prefix += [LOVED]

            new_title = f"{" ".join(prefix)} {title}" if prefix else title

            if new_title != original_title:
                print(f"Renaming \"{original_title}\" to \"{new_title}\"")
                await message.edit_caption(caption="\n".join([new_title] + rest), parse_mode=enums.ParseMode.MARKDOWN)

        text = ""

        def append_game(game, last):
            nonlocal text
            (title, link, loved) = game
            loved = {True: LOVED + " ", False: ""}[loved]
            prefix = "└─" if last else "├─"
            text += f"  `{prefix}` {loved}{title} [↗]({link})\n"

        def append_title(title):
            nonlocal text
            text += f"\n**{title}**\n"

        categories = [
            (IN_PROGRESS + " In Progress", games[IN_PROGRESS]),
            (TODO + " Todo", games[TODO]),
            (COMPLETED + " Completed", games[COMPLETED]),
            (DROPPED + " Dropped", games[DROPPED]),
            (SCORING + " Scoring", games[SCORING]),
            (APP + " Apps", games[APP]),
        ]

        for (title, games) in categories:
            games.reverse()
            append_title(title)
            for game in games:
                append_game(game, game == games[-1])

        print(str(int(len(text) / 4096 * 100)) + "%")

        try:
            await app.edit_message_text(
                chat_id=getenv("CHANNEL_ID"),
                message_id=int(getenv("REPORT_MESSAGE_ID")),
                text=text,
                parse_mode=enums.ParseMode.MARKDOWN
            )
        except errors.MessageNotModified:
            None


app.run(main())
