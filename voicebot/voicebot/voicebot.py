# bots/voice_bot.py

import asyncio
from botbuilder.core import (
    ActivityHandler, TurnContext,
    ConversationState, MemoryStorage
)
from botbuilder.dialogs import (
    DialogSet, DialogTurnStatus, TextPrompt
)
from dialogs.registration_dialog import RegistrationDialog
from services.db import get_all_users
from services.speech_handler import listen, speak

_memory = MemoryStorage()
_conversation = ConversationState(_memory)

class VoiceBot(ActivityHandler):
    def __init__(self):
        self.dialog_state = _conversation.create_property("DialogState")
        self.dialogs = DialogSet(self.dialog_state)
        self.dialogs.add(TextPrompt("text"))
        self.dialogs.add(RegistrationDialog())

    async def on_members_added_activity(self, members_added, turn: TurnContext):
        for member in members_added:
            if member.id != turn.activity.recipient.id:
                speak("Hello! I'm your registration bot. Let's get started!")
                await turn.send_activity("Hello! 👋 I'm your registration bot — let’s get started!")

    async def on_members_added_activity(self, members_added, turn: TurnContext):
        for member in members_added:
            if member.id != turn.activity.recipient.id:
                speak("Hello! I'm your registration bot. Let's get started!")
                await turn.send_activity("Hello! 👋 I'm your registration bot — let’s get started!")

    async def on_message_activity(self, turn: TurnContext):
        dialog_context = await self.dialogs.create_context(turn)
        result = await dialog_context.continue_dialog()

        if result.status == DialogTurnStatus.Empty:
            # Стартуем регистрацию, если она ещё не начата
            speak("Let's start your registration. What’s your first name?")
            await dialog_context.begin_dialog("register")
            await _conversation.save_changes(turn)
            return
        # Диалоговая логика
        dialog_context = await self.dialogs.create_context(turn)
        result = await dialog_context.continue_dialog()

        if result.status == DialogTurnStatus.Empty:
            speak("Let's start your registration. What’s your first name?")
            await dialog_context.begin_dialog("register")

        await _conversation.save_changes(turn)
