import os
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from voicebot.voicebot import VoiceBot

# -----------------------------------------------------------------------------
# 1) Configuration: read credentials from environment variables
# -----------------------------------------------------------------------------
APP_ID = os.environ.get("MICROSOFT_APP_ID")
if not APP_ID:
    raise Exception("❌ Environment variable MICROSOFT_APP_ID not found")

APP_PASSWORD = os.environ.get("MICROSOFT_APP_PASSWORD")
if not APP_PASSWORD:
    raise Exception("❌ Environment variable MICROSOFT_APP_PASSWORD not found")
APP_PASSWORD = os.environ["MICROSOFT_APP_PASSWORD"]
PORT = int(os.environ.get("PORT", 3978))

# -----------------------------------------------------------------------------
# 2) Create the Bot Framework Adapter
# -----------------------------------------------------------------------------
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# -----------------------------------------------------------------------------
# 3) Instantiate your bot
# -----------------------------------------------------------------------------
bot = VoiceBot()

# -----------------------------------------------------------------------------
# 4) Message handler for /api/messages
# -----------------------------------------------------------------------------
async def messages(req: web.Request) -> web.Response:
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    try:
        await adapter.process_activity(activity, auth_header, bot.on_turn)
        return web.Response(status=200)
    except Exception as e:
        # Log the error and return 500
        print("❌ Error handling activity:", e)
        return web.Response(status=500, text=str(e))

# -----------------------------------------------------------------------------
# 5) Start the aiohttp web app
# -----------------------------------------------------------------------------
app = web.Application()
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    print(f"Starting server on port {PORT}...")
    web.run_app(app, host="0.0.0.0", port=PORT)
