import requests
from src.dbservice import DBService
from src.entities.unoreverse import UnoReverse
from random import randint
from twitchAPI import EventSub, Twitch, CustomRewardRedemptionStatus


class TwitchTimeoutBattle:
    __roulette_reward_id = "twitch-timeout-battle-roulette-reward-id"
    __uno_reverse_reward_id = "twitch-timeout-battle-uno-reverse-reward-id"
    __timeout_reward_id = "twitch-timeout-battle-timeout-reward-id"

    __fullfilled = CustomRewardRedemptionStatus.FULFILLED
    __canceled = CustomRewardRedemptionStatus.CANCELED

    def __init__(self, db_service: DBService, twitch_api: Twitch, twitch_hook: EventSub, moderator_id: str):
        self.__twitch_hook = twitch_hook
        self.__twitch_api = twitch_api
        self.__moderator_id = moderator_id
        self.__db_service = db_service

    def subscribe(self, broadcaster_user_id):
        self.unsubscribe()
        self.__twitch_hook.start()

        self.__twitch_hook.listen_channel_points_custom_reward_redemption_add(
            broadcaster_user_id, self.__roulette, self.__roulette_reward_id)
        self.__twitch_hook.listen_channel_points_custom_reward_redemption_add(
            broadcaster_user_id, self.__uno_reverse, self.__uno_reverse_reward_id)
        self.__twitch_hook.listen_channel_points_custom_reward_redemption_add(
            broadcaster_user_id, self.__timeout_someone, self.__timeout_reward_id)

    def unsubscribe(self):
        self.__twitch_hook.unsubscribe_all()

    def __roulette(self, data):
        broadcaster_id, reward_id, user_id, user_name = self.__parse_data(data)

        alive = bool(randint(0, 7))
        status = self.__canceled if alive else self.__fullfilled
        self.__twitch_api.update_redemption_status(
            broadcaster_id, reward_id, [self.__roulette_reward_id], status)
        if not alive:
            self.__twitch_api.ban_user(
                broadcaster_id, self.__moderator_id, user_id, f"{user_name} did that to himself", 600)

    def __uno_reverse(self, data):
        broadcaster_id, reward_id, user_id, user_name = self.__parse_data(data)

        uno_reverse = self.__db_service.get_uno_reverse_by_id(
            broadcaster_id, user_id)
        if uno_reverse is None:
            uno_reverse = UnoReverse(
                broadcaster_id=broadcaster_id,
                user_id=user_id,
                user_name=user_name,
                count=1)
            self.__db_service.add_uno_reverse(uno_reverse)
        else:
            uno_reverse.count += 1
            self.__db_service.update_uno_reverse(uno_reverse)

        self.__twitch_api.update_redemption_status(
            broadcaster_id, reward_id, [self.__uno_reverse_reward_id], self.__fullfilled)

    def __timeout_someone(self, data):
        broadcaster_id, reward_id, user_id, user_name = self.__parse_data(data)
        user_input = data["user_input"]

        viewers, untimeoutables = self.__get_chatters(broadcaster_id)

        targets = [user for user in user_input.replace(
            "@", "").split(" ") if user in viewers and user not in untimeoutables]
        if not targets:
            self.__twitch_api.update_redemption_status(
                broadcaster_id, reward_id, [self.__timeout_reward_id], self.__canceled)
            return
        users = self.__twitch_api.get_users(logins=[targets[0]])["data"]
        if not users:
            self.__twitch_api.update_redemption_status(
                broadcaster_id, reward_id, [self.__timeout_reward_id], self.__canceled)
            return
        defender_user = users[0]
        defender_id = defender_user["id"]
        defender_user_name = defender_user["login"]

        attacker = self.__db_service.get_uno_reverse_by_id(
            broadcaster_id, user_id)
        if attacker is None:
            attacker = UnoReverse(broadcaster_id=broadcaster_id, user_id=user_id, user_name=user_name,
                                  count=0)
            self.__db_service.add_uno_reverse(attacker)

        defender = self.__db_service.get_uno_reverse_by_id(
            broadcaster_id, defender_id)

        if defender is None:
            defender = UnoReverse(broadcaster_id=broadcaster_id, user_id=defender_id, user_name=defender_user_name,
                                  count=0)
            self.__db_service.add_uno_reverse(defender)

        min_uno = min(attacker.count, defender.count)
        defender.count -= min_uno
        attacker.count -= min_uno
        self.__db_service.commit()

        loser = min(defender, attacker,
                    key=lambda ur: ur.count)
        self.__twitch_api.ban_user(
            broadcaster_id, self.__moderator_id, loser, f"{loser.user_name} in the timeout battle from {attacker.user_name} to {defender.user_name}", 600)
        self.__twitch_api.update_redemption_status(
            broadcaster_id, reward_id, [self.__timeout_reward_id], self.__fullfilled)

    def __parse_data(self, data):
        broadcaster_id = data["broadcaster_user_id"]
        reward_id = data["id"]
        user_id = data["user_id"]
        user_name = data["user_name"]

        return broadcaster_id, reward_id, user_id, user_name

    def __get_chatters(self, broadcaster_id):
        chatters = requests.get(
            f"https://tmi.twitch.tv/group/user/{broadcaster_id}/chatters").json()["chatters"]

        viewers = set(chatters["viewers"])
        untimeoutables = set(chatters["broadcaster"] +
                             chatters["vips"] +
                             chatters["moderators"] +
                             chatters["staff"] +
                             chatters["admins"] +
                             chatters["global_mods"])

        return viewers, untimeoutables
