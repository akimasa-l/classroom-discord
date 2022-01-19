import os.path
import morokoshi_token

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import discord
import datetime
import json

TOKEN = morokoshi_token.TOKEN
client = discord.Client()

# 起動時に動作する処理


@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    await create_embed()
    # print('ログインしました')


# Botの起動とDiscordサーバーへの接続

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
          "https://www.googleapis.com/auth/classroom.announcements.readonly",
          "https://www.googleapis.com/auth/classroom.rosters.readonly",
          "https://www.googleapis.com/auth/classroom.profile.emails",
          "https://www.googleapis.com/auth/classroom.rosters",
          "https://www.googleapis.com/auth/classroom.profile.photos"]


def is_same_announcement(announcement) -> bool:
    if os.path.exists("./announcement_url.txt"):
        with open("./announcement_url.txt") as f:
            if f.read() == announcement["url"]:
                return True
    with open("./announcement_url.txt", mode="w") as f:
        f.write(announcement["url"])
    return False


def to_better_json(announcement):
    creationTime = datetime.datetime.fromisoformat(
        announcement['creationTime'].replace('Z', '+00:00'))
    updateTime = datetime.datetime.fromisoformat(
        announcement['updateTime'].replace('Z', '+00:00'))
    title, *text = announcement["text"].split("\n")
    return {"title": title,
            "text": "\n".join(text),
            "url": announcement["alternateLink"],
            "creationTime": creationTime,
            "updateTime": updateTime
            }


# https://developers.google.com/classroom/quickstart/python
# ↑ここ見ればだいたい分かる
def getClassroomInfo():
    """Shows basic usage of the Classroom API.
    Prints the names of the first 10 courses the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('classroom', 'v1', credentials=creds)
        results = service.courses().announcements().list(
            courseId="1333776954", pageSize=1,
        ).execute()
        # print(results)
        announcement = results.get("announcements", [])[0]
        userId = announcement["creatorUserId"]
        results = service.userProfiles().get(userId=userId).execute()
        return [to_better_json(announcement), results]

    except HttpError as error:
        print('An error occurred: %s' % error)


async def create_embed():
    announcement, author = getClassroomInfo()
    if is_same_announcement(announcement):
        await client.close()
        return
    # ここを見た
    # https://qiita.com/hisuie08/items/5b63924156080694fc81
    embed = discord.Embed(  # Embedを定義する
        title=announcement["title"],  # タイトル
        color=0x00ff00,  # フレーム色指定(今回は緑)
        description=announcement["text"],  # Embedの説明文 必要に応じて
        url=announcement["url"]  # これを設定すると、タイトルが指定URLへのリンクになる
    )
    embed.set_author(name=author["name"]["fullName"],
                     url="https://github.com/akimasa-l/classroom-discord",
                     icon_url=f"""https:{author["photoUrl"]}"""
                     )
    embed.set_image(url="https://lh3.googleusercontent.com/-Dd8q9n-JKGs/XsICByZYRqI/AAAAAAAAAFA/roSOgvQ3HXsbwIZF3HcI_nw0Nt8pqabOwCLcBGAsYHQ/s1280-fcrop64=1,0118744bff72c9df/IMG_2254.JPG",)
    embed.set_footer(
        text=f"""{announcement["creationTime"].strftime('%Y年%m月%d日 %H時%M分')} (最終更新: {announcement["updateTime"].strftime('%Y年%m月%d日 %H時%M分')})""")
    channel = await client.fetch_channel(morokoshi_token.CHANNEL_ID)
    await channel.send(embed=embed)
    await client.close()

if __name__ == '__main__':
    client.run(TOKEN)
