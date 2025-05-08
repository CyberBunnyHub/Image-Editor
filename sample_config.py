# By @TroJanzHEX


import os


class Config(object):
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7850386310:AAEeCeBvPdkwThjHSOjHecEhWfzI4DQ8JsM")

    APP_ID = int(os.environ.get("APP_ID", "14853951"))

    API_HASH = os.environ.get("API_HASH", "0a33bc287078d4dace12aaecc8e73545")

    # Get this api from https://www.remove.bg/b/background-removal-api
    RemoveBG_API = os.environ.get("RemoveBG_API", "vzxJSig9pi5j4xvDX3ykqzyc")
