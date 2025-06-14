from botbuilder.core import ActivityHandler, TurnContext

class VoiceBot(ActivityHandler):
    def __init__(self):
        self.conversations = {}

    async def on_message_activity(self, turn_context: TurnContext):
        user_id = turn_context.activity.from_property.id

        if user_id not in self.conversations:
            self.conversations[user_id] = {
                "step": "ask_name",
                "data": {}
            }

        user_data = self.conversations[user_id]
        step = user_data["step"]
        text = turn_context.activity.text.strip()

        if step == "ask_name":
            await turn_context.send_activity("Hi! What's your full name?")
            user_data["step"] = "get_name"

        elif step == "get_name":
            user_data["data"]["name"] = text
            await turn_context.send_activity("Got it. What's your birthdate? (YYYY-MM-DD)")
            user_data["step"] = "get_birthdate"

        elif step == "get_birthdate":
            user_data["data"]["birthdate"] = text
            await turn_context.send_activity("Great. What's your email?")
            user_data["step"] = "get_email"

        elif step == "get_email":
            user_data["data"]["email"] = text
            await turn_context.send_activity("Thanks! Your registration info has been collected:")
            await turn_context.send_activity(str(user_data["data"]))
            user_data["step"] = "done"

        else:
            await turn_context.send_activity("You’ve already registered. Thanks!")
