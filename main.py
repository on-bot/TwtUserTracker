# Imports
import tweepy
import os
import time
import collections
from discord_webhook import DiscordWebhook, DiscordEmbed
from pymongo import MongoClient

# Importing Database
cluster = MongoClient(os.environ["MONGO_API"])
db = cluster["discord"]
collection = db["twitter followings"]
ollection2 = db["config"]

# Getting config datas
config = collection2.find_one({"_id": 0})

# Twitter auth
client = tweepy.Client(bearer_token=config['twitter_credentials']['bearer_token'],
                       consumer_key=config['twitter_credentials']['consumer_key'],
                       consumer_secret=config['twitter_credentials']['consumer_secret'],
                       access_token=config['twitter_credentials']['access_token'],
                       access_token_secret=config['twitter_credentials']['access_token_secret'],
                       wait_on_rate_limit=True)

auth = tweepy.OAuth1UserHandler(config['twitter_credentials']['consumer_key'],
                                config['twitter_credentials']['consumer_secret'],
                                config['twitter_credentials']['access_token'],
                                config['twitter_credentials']['access_token_secret'])


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


def send_embed_message(victim, user, url):
    followers = get_follower_count(user)
    webhook = DiscordWebhook(url=url)
    embed = DiscordEmbed(color=242424, title=f"{victim} just Followed {user}", url=f"https://twitter.com/{user}")
    embed.set_thumbnail(url=get_avatar_url(user))
    embed.add_embed_field(name="\u200b", value=f"**{user}** has {followers} followers")
    embed.set_timestamp()
    embed.set_footer(text='\u200b')
    webhook.add_embed(embed)
    response = webhook.execute()


def send_log(victim, url):
    webhook = DiscordWebhook(url=url, content=f"Checking if {victim} followed any users")
    response = webhook.execute()


def send_message(message, url):
    webhook = DiscordWebhook(url=url, content=message)
    response = webhook.execute()


# General Function
def is_empty():
    try:
        cur = collection.find()
        results = list(cur)
        if len(results) == 0:
            return True
        else:
            return False
    except:
        return True


def is_same(list1, list2):
    if collections.Counter(list1) == collections.Counter(list2):
        return True
    return False


# Polling Twitter Followings
while 1:
    victims = collection.find_one({"_id": 0})['victims']
    delay = 60
    if is_empty():
        for i in victims:
            post = {"_id": i, "followings": scrape_user_friends(i)}
            collection.insert_one(post)
            time.sleep(delay)
    else:
        victim_followings_ids = collection.find().distinct('_id')
        for i in victims:
            if i not in victim_followings_ids:
                post = {"_id": i, "followings": scrape_user_friends(i)}
                collection.insert_one(post)
                time.sleep(delay)

        del_list = [i for i in victim_followings_ids if i not in victims]

        for i in del_list:
            collection.delete_one({"_id": i})

    for i in victims:
        print(f"checking: {i}")
        send_log(i, os.environ["LOG_WEBHOOK"])
        send_log(i, os.environ["SEC_LOG_WEBHOOK"])
        victim_new_followings_ids = scrape_user_friends(i)
        victim_followings_ids = collection.find_one({"_id": i})['followings']
        collection.update_one({"_id": i}, {"$set": {"followings": victim_new_followings_ids}})
        if is_same(victim_new_followings_ids, victim_followings_ids):
            new_users = []
        else:
            new_users = []
            for user in victim_new_followings_ids:
                if user not in victim_followings_ids:
                    try:
                        new_users.append(get_screen_name(user))
                    except:
                        send_message(f"{user} was followed", os.environ['MAIN_WEBHOOK'])
        for user in new_users:
            send_embed_message(i, user, os.environ["MAIN_WEBHOOK"])
            send_embed_message(i, user, os.environ["SEC_WEBHOOK"])
            print(f"detected: {user}")
        time.sleep(delay)
    time.sleep(2)

