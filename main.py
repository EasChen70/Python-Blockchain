import tweepy
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="secret.env")

#Authentication
api_key = os.getenv("api_key")
api_secret = os.getenv("api_secret")
bearer_token = os.getenv("bearer_token")
access_token = os.getenv("access_token")
access_token_secret = os.getenv("access_token_secret")


auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

api.update_status(status="Hello")
