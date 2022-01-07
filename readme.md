# Google Classroom Notifier for Discord

classroomになにか投稿されたらdiscordに通知が行くようにしたいです！！

# やるべきこと

1. <https://console.cloud.google.com/apis/library/classroom.googleapis.com> に行って API を有効にしたりプロジェクトを作成したりする

1. <https://console.cloud.google.com/apis/credentials> で OAuth クライアント ID を作成して json をダウンロードして `credentials.json` って名前をつける

1. `morokoshi_token.example.py` をコピーして `morokoshi_token.py` に名前を変える

1. `morokoshi_token.py` に discord の bot の token を入れる

1. `quickstart.py` を実行してみて確かめる