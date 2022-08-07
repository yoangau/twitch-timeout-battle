from twitchAPI import EventSub, Twitch, CustomRewardRedemptionStatus
from random import randint
import requests


class TwitchTimeoutBattle:
    __roulette_reward_id = "twitch-timeout-battle-roulette-reward-id"
    __uno_reverse_reward_id = "twitch-timeout-battle-uno-reverse-reward-id"
    __timeout_reward_id = "twitch-timeout-battle-timeout-reward-id"

    __fullfilled = CustomRewardRedemptionStatus.FULFILLED
    __canceled = CustomRewardRedemptionStatus.CANCELED

    def __init__(self, twitch_api: Twitch, twitch_hook: EventSub, moderator_id: str):
        self.__twitch_hook = twitch_hook
        self.__twitch_api = twitch_api
        self.__moderator_id = moderator_id

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
        self.__twitch_hook.stop()

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
        print("add to db", broadcaster_id,
              reward_id, user_id, user_name)  # todo
        self.__twitch_api.update_redemption_status(
            broadcaster_id, reward_id, [self.__roulette_reward_id], self.__fullfilled)

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

        attacker = user_id
        defender = targets[0]

        attacker_uno = 2  # todo
        defender_uno = 1

        min_uno = min(attacker_uno, defender_uno)
        attacker_uno -= min_uno  # todo save new values to db
        defender_uno -= min_uno

        loser, loser_uno = min(((defender, defender_uno), (attacker, attacker_uno)),
                               key=lambda x: x[1])
        self.__twitch_api.ban_user(
            broadcaster_id, self.__moderator_id, loser, f"{loser} in the timeout battle from {attacker} to {defender}", 600)
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
