import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, text

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope

from src.eventsub import test

load_dotenv()

twitch_app_secret = os.environ.get("TWITCH_APP_SECRET")
twitch_client_id = os.environ.get("TWITCH_CLIENT_ID")

twitch = Twitch(twitch_client_id, twitch_app_secret)

# Timeout user
# twitch.ban_user(broadcaster_id, moderator_id, user_id, reason, duration=600)


# user_info = twitch.get_users(logins=['octoio'])
# user_id = user_info['data'][0]['id']
# print(user_id, user_info)
# For testing ":memory:" instead of db path
db_path = "db/timeout-battle.sqlite3"
engine = create_engine(f"sqlite+pysqlite:///{db_path}", echo=True, future=True)
with engine.connect() as conn:
    result = conn.execute(text("select 'hello world'"))
    print(result.all())

if __name__ == "__main__":
    pass
