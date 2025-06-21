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
        # Коннект к Azure SQL Database
        conn_str = os.environ.get("SQL_CONNECTION_STRING")
        self.db = pyodbc.connect(conn_str)

        # Хранилище состояния диалога (в реальном приложении используйте ConversationState)
        self.dialog_state = {}

        # Набор диалогов
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
        # 1) Proactive welcome при подключении
        if turn_context.activity.type == ActivityTypes.conversation_update:
            for member in turn_context.activity.members_added:
                if member.id != turn_context.activity.recipient.id:
                    await turn_context.send_activity(
                        MessageFactory.text(
                            "Hello! 👋\nI’m your voice registration bot.\nMay I know your name?"
                        )
                    )
            return  # не дальше по диалогам, это только приветствие

        # 2) Обработка обычных сообщений
        if turn_context.activity.type == ActivityTypes.message:
            dc = await self.dialogs.create_context(turn_context)
            result = await dc.continue_dialog()
            if result.status == DialogTurnStatus.Empty:
                await dc.begin_dialog("regDialog")

        # 3) (опционально) очистка очереди отправки
        await turn_context.send_activities([])

    # Шаги WaterfallDialog

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

        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO Users (name, email, phone, address) VALUES (?, ?, ?, ?)",
            name, email, phone, address
        )
        self.db.commit()

        await step.context.send_activity(
            MessageFactory.text(f"Thank you, {name}! You’re all set. 🎉")
        )
        return await step.end_dialog()
