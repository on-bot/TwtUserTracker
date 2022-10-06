# Imports
import tweepy
import json
import os
import time
import collections
from discord_webhook import DiscordWebhook, DiscordEmbed

# Getting config datas
conf = open("./config/config.json")
config = json.load(conf)

# Twitter auth
client = tweepy.Client(bearer_token=os.environ["BEARER_TOKEN"],
                       consumer_key=os.environ["CONSUMER_KEY"],
                       consumer_secret=os.environ["CONSUMER_SECRET"],
                       access_token=os.environ["ACCESS_TOKEN"],
                       access_token_secret=os.environ["ACCESS_TOKEN_SECRET"],
                       wait_on_rate_limit=True)

auth = tweepy.OAuth1UserHandler(os.environ["CONSUMER_KEY"],
                                os.environ["CONSUMER_SECRET"],
                                os.environ["ACCESS_TOKEN"],
                                os.environ["ACCESS_TOKEN_SECRET"])


api = tweepy.API(auth, wait_on_rate_limit=True)


# Twitter Functions
def scrape_user_friends(username):
    friends_scraped = []
    for i, _id in enumerate(tweepy.Cursor(api.get_friend_ids, screen_name=username).items()):
        friends_scraped.append(_id)
    return friends_scraped


def get_screen_name(id):
    return api.get_user(user_id=int(id)).screen_name


def get_avatar_url(username):
    userobject = api.get_user(screen_name=username)
    return userobject.profile_image_url


def get_follower_count(username):
    userobject = api.get_user(screen_name=username)
    return userobject.followers_count


def send_message(victim, user, url):
    followers = get_follower_count(user)
    webhook = DiscordWebhook(url=url)
    embed = DiscordEmbed(color=242424, title=f"{victim} just Followed {user}", url=f"https://twitter.com/{user}")
    embed.set_thumbnail(url=get_avatar_url(victim))
    embed.add_embed_field(name="\u200b", value=f"**{user}** has {followers} followers")
    embed.set_timestamp()
    embed.set_footer(text='\u200b')
    webhook.add_embed(embed)
    response = webhook.execute()


def send_log(victim, url):
    webhook = DiscordWebhook(url=url, content=f"Checking if {victim} followed any users")
    response = webhook.execute()


# General Function
def is_empty(file):
    try:
        with open(file, 'r') as f:
            if f.read(2) == '[]':
                return True
            return False
    except:
        return True


def is_same(list1, list2):
    if collections.Counter(list1) == collections.Counter(list2):
        return True
    return False


# Polling Twitter Followings
while 1:
    conf = open("./config/config.json")
    config = json.load(conf)
    victims = config['victims']
    delay = 60
    if is_empty('./data/temp.json'):
        victim_followings_ids = {}
        for i in victims:
            victim_followings_ids[i] = scrape_user_friends(i)
            time.sleep(delay)
        json_obj = json.dumps(victim_followings_ids, indent=4)
        with open('./data/temp.json', 'w') as f:
            f.write(json_obj)
    else:
        victim_followings_ids = json.load(open('./data/temp.json'))
        for i in victims:
            if i not in victim_followings_ids.keys():
                victim_followings_ids[i] = scrape_user_friends(i)
                time.sleep(delay)
        del_list = [i for i in victim_followings_ids.keys() if i not in victims]

        for i in del_list:
            del victim_followings_ids[i]

        json_obj = json.dumps(victim_followings_ids, indent=4)
        with open('./data/temp.json', 'w') as f:
            f.write(json_obj)

    victim_new_followings_ids = {}
    for i in victims:
        send_log(i, os.environ["LOG_WEBHOOK"])
        victim_new_followings_ids[i] = scrape_user_friends(i)
        if is_same(victim_new_followings_ids[i], victim_followings_ids[i]):
            new_users = []
        else:
            new_users = []
            for user in victim_new_followings_ids[i]:
                if user not in victim_followings_ids[i]:
                    new_users.append(get_screen_name(user))
        for user in new_users:
            send_message(i, user, os.environ["MAIN_WEBHOOK"])
        time.sleep(delay)
    json_obj = json.dumps(victim_new_followings_ids, indent=4)
    with open('./data/temp.json', 'w') as f:
        f.write(json_obj)
    time.sleep(2)

