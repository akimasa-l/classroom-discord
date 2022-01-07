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
    channel = await client.fetch_channel(morokoshi_token.CHANNEL_ID)
    embed = discord.Embed(  # Embedを定義する
        title="Example Embed",  # タイトル
        color=0x00ff00,  # フレーム色指定(今回は緑)
        description="Example Embed for Advent Calendar",  # Embedの説明文 必要に応じて
        url="https://example.com"  # これを設定すると、タイトルが指定URLへのリンクになる
    )
    await channel.send(embed=create_embed())
    print('ログインしました')


# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    if message.content == 'たんたん大好き':
        await message.channel.send(embed=create_embed())

# Botの起動とDiscordサーバーへの接続

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
          "https://www.googleapis.com/auth/classroom.announcements.readonly"]


def to_better_json(classroomInfo):
    creationTime = datetime.datetime.fromisoformat(
        classroomInfo['creationTime'].replace('Z', '+00:00'))
    updateTime = datetime.datetime.fromisoformat(
        classroomInfo['updateTime'].replace('Z', '+00:00'))
    title, *text = classroomInfo["text"].split("\n")
    return {"title": title,
            "text": "\n".join(text),
            "url": classroomInfo["alternateLink"],
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

        """ # Call the Classroom API
        results = service.courses().list(pageSize=50).execute()
        courses = results.get('courses', [])

        if not courses:
            print('No courses found.')
            return
        # Prints the names of the first 10 courses.
        print('Courses:')
        for course in courses:
            print(course['name'])
            print(course) """
        results = service.courses().announcements().list(
            courseId="1333776954", pageSize=1,
        ).execute()
        # print(results)
        return results.get("announcements", [])[0]

    except HttpError as error:
        print('An error occurred: %s' % error)


def create_embed():
    classroomInfo = to_better_json(getClassroomInfo())
    # ここを見た
    # https://qiita.com/hisuie08/items/5b63924156080694fc81
    embed = discord.Embed(  # Embedを定義する
        title=classroomInfo["title"],  # タイトル
        color=0x00ff00,  # フレーム色指定(今回は緑)
        description=classroomInfo["text"],  # Embedの説明文 必要に応じて
        url=classroomInfo["url"]  # これを設定すると、タイトルが指定URLへのリンクになる
    )
    embed.set_author(name=client.user,  # Botのユーザー名
                     # titleのurlのようにnameをリンクにできる。botのWebサイトとかGithubとか
                     url="https://github.com/akimasa-l/classroom-discord",
                     icon_url=client.user.avatar_url  # Botのアイコンを設定してみる
                     )
    embed.set_image(url="https://lh3.googleusercontent.com/-Dd8q9n-JKGs/XsICByZYRqI/AAAAAAAAAFA/roSOgvQ3HXsbwIZF3HcI_nw0Nt8pqabOwCLcBGAsYHQ/s1280-fcrop64=1,0118744bff72c9df/IMG_2254.JPG",)
    embed.set_footer(text=f"""{classroomInfo["creationTime"].strftime('%Y年%m月%d日 %H時%M分')} (最終更新: {classroomInfo["updateTime"].strftime('%Y年%m月%d日 %H時%M分')})""")
    return embed



if __name__ == '__main__':
    client.run(TOKEN)
