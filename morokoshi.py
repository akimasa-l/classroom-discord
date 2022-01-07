import os.path
import morokoshi_token

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import discord
import json

TOKEN = morokoshi_token.TOKEN
client = discord.Client()

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')
    client.channels.cache.get("928869947885633577").send(getClassroomInfo())

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    if message.content == 'たんたん大好き':
        await message.channel.send(getClassroomInfo())

# Botの起動とDiscordサーバーへの接続

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',"https://www.googleapis.com/auth/classroom.announcements.readonly"]


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
        results = service.courses().announcements().list(courseId="1333776954",pageSize=1).execute()
        print(results)
        return results.get("announcements", [])[0]
        

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    client.run(TOKEN)