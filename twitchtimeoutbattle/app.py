import os
from dotenv import load_dotenv

from twitchAPI import Twitch, EventSub, AuthScope, UserAuthenticator

from src.dbservice import DBService
from src.twitchtimeoutbattle import TwitchTimeoutBattle
from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


load_dotenv()

twitch_app_secret = os.environ.get("TWITCH_APP_SECRET")
twitch_client_id = os.environ.get("TWITCH_CLIENT_ID")
db_path = os.environ.get("DB_PATH")
webhook_url = os.environ.get("WEBHOOK_URL")

target_scope = [AuthScope.MODERATOR_MANAGE_BANNED_USERS,
                AuthScope.CHANNEL_MANAGE_REDEMPTIONS]

if __name__ == "__main__":
    db_service = DBService(db_path)
    twitch_api = Twitch(twitch_client_id, twitch_app_secret)
    twitch_api.authenticate_app([])
    auth = UserAuthenticator(twitch_api, target_scope, force_verify=False)
    token, refresh_token = auth.authenticate()

    twitch_api.set_user_authentication(token, target_scope, refresh_token)

    twitch_hook = EventSub(webhook_url, twitch_client_id, 5001, twitch_api)
    TwitchTimeoutBattle(db_service, twitch_api, twitch_hook, 95089557)
    app.run(debug=True)
