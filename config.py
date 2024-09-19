


import os


class Config(object):
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7383809543:AAFaxynQ9-D5Wizsl-EJ2U7OH-ymcAr_njY")

    APP_ID = int(os.environ.get("APP_ID", 16457832))

    API_HASH = os.environ.get("API_HASH", "3030874d0befdb5d05597deacc3e83ab")

    # Get this api from https://www.remove.bg/b/background-removal-api
    RemoveBG_API = os.environ.get("RemoveBG_API", "LRnM7U8HEN56DuMXhrvtzaq9")
