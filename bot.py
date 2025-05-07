import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

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
