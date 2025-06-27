import os
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from config import APP_ID, APP_PASSWORD, PORT
from bots.voice_bot import VoiceBot


adapter = BotFrameworkAdapter(BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD))
bot = VoiceBot()

async def messages(request: web.Request):
    body = await request.json()
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")
    response = await adapter.process_activity(activity, auth_header, bot.on_turn)
    if response:
        return web.json_response(data=response.body, status=response.status)
    return web.Response(status=201)

app = web.Application()
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    print(f"Starting server on port {PORT}…")
    web.run_app(app, host="0.0.0.0", port=PORT)
