import os
import pyodbc
from botbuilder.core import TurnContext, MessageFactory
from botbuilder.schema import ActivityTypes
from botbuilder.dialogs import (
    DialogSet,
    DialogTurnStatus,
    WaterfallDialog,
    WaterfallStepContext,
    TextPrompt
)
from botbuilder.dialogs.prompts import PromptOptions

class VoiceBot:
    def __init__(self):
        # Connect to Azure SQL Database with error handling
        conn_str = os.environ.get("SQL_CONNECTION_STRING")
        try:
            self.db = pyodbc.connect(conn_str)
            print("✅ Connected to database.")
        except Exception as e:
            print("❌ Database connection failed:", e)
            self.db = None

        # Dialog state and dialogs setup
        self.dialog_state = {}
        self.dialogs = DialogSet(self.dialog_state)
        self.dialogs.add(TextPrompt("namePrompt"))
        self.dialogs.add(TextPrompt("emailPrompt"))
        self.dialogs.add(TextPrompt("phonePrompt"))
        self.dialogs.add(TextPrompt("addressPrompt"))
        self.dialogs.add(
            WaterfallDialog(
                "regDialog",
                [
                    self.ask_name,
                    self.ask_email,
                    self.ask_phone,
                    self.ask_address,
                    self.save_user,
                ],
            )
        )

    async def on_turn(self, turn_context: TurnContext):
        print(f"🔹 Activity type: {turn_context.activity.type}")

        if turn_context.activity.type == ActivityTypes.conversation_update:
            for member in turn_context.activity.members_added:
                print("🔸 New member:", member.id)
                if member.id != turn_context.activity.recipient.id:
                    await turn_context.send_activity(
                        MessageFactory.text(
                            "Hello! 👋\nI’m your voice registration bot.\nMay I know your name?"
                        )
                    )
            return

        if turn_context.activity.type == ActivityTypes.message:
            print("🔹 User said:", turn_context.activity.text)
            dc = await self.dialogs.create_context(turn_context)
            result = await dc.continue_dialog()
            if result.status == DialogTurnStatus.Empty:
                await dc.begin_dialog("regDialog")

        await turn_context.send_activities([])

    async def ask_name(self, step: WaterfallStepContext):
        return await step.prompt(
            "namePrompt",
            PromptOptions(prompt=MessageFactory.text("What’s your name?"))
        )

    async def ask_email(self, step: WaterfallStepContext):
        step.values["name"] = step.result
        return await step.prompt(
            "emailPrompt",
            PromptOptions(prompt=MessageFactory.text("Thanks! What’s your email?"))
        )

    async def ask_phone(self, step: WaterfallStepContext):
        step.values["email"] = step.result
        return await step.prompt(
            "phonePrompt",
            PromptOptions(prompt=MessageFactory.text("Great. And your phone number?"))
        )

    async def ask_address(self, step: WaterfallStepContext):
        step.values["phone"] = step.result
        return await step.prompt(
            "addressPrompt",
            PromptOptions(prompt=MessageFactory.text("Finally, what’s your address?"))
        )

    async def save_user(self, step: WaterfallStepContext):
        name    = step.values["name"]
        email   = step.values["email"]
        phone   = step.values["phone"]
        address = step.result

        if self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute(
                    "INSERT INTO Users (name, email, phone, address) VALUES (?, ?, ?, ?)",
                    name, email, phone, address
                )
                self.db.commit()
                print("✅ User saved to database.")
            except Exception as e:
                print("❌ Error saving user to DB:", e)

        await step.context.send_activity(
            MessageFactory.text(f"Thank you, {name}! You’re all set. 🎉")
        )
        return await step.end_dialog()
