def run_bot():
    print("Bot is running...")
    
    import threading
from flask import Flask
import os

# Run Flask dummy server in a thread
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram bot running on Render."

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Start dummy web server in background
    threading.Thread(target=run_flask).start()



# By @TroJanzHEX
from pyrogram import Client
import os

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config  # pylint:disable=import-error


if __name__ == "__main__":
    plugins = dict(root="plugins")

    app = Client(
        "TroJanz",
        bot_token=Config.TG_BOT_TOKEN,
        api_id=Config.APP_ID,
        api_hash=Config.API_HASH,
        plugins=plugins,
        workers=300,
    )
    app.run()
