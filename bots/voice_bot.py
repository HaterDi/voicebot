# voicebot/bots/voice_bot.py
from botbuilder.core import (
    ActivityHandler, TurnContext,
    ConversationState, MemoryStorage
)
from botbuilder.dialogs import (
    DialogSet, DialogTurnStatus, TextPrompt
)
from dialogs.registration_dialog import RegistrationDialog

# ----------- состояние ------------------------------------------------
_memory         = MemoryStorage()
_conversation   = ConversationState(_memory)

class VoiceBot(ActivityHandler):
    """Основной бот-класс. Запускает Waterfall-регистрацию."""

    def __init__(self):
        self.dialog_state = _conversation.create_property("DialogState")
        self.dialogs = DialogSet(self.dialog_state)
        self.dialogs.add(TextPrompt("text"))
        self.dialogs.add(RegistrationDialog())

    # приветствие новых юзеров
    async def on_members_added_activity(self, members_added, turn: TurnContext):
        for m in members_added:
            if m.id != turn.activity.recipient.id:
                await turn.send_activity(
                    "Hello! 👋 I'm your registration bot — let's get started!"
                )
                dc = await self.dialogs.create_context(turn)
                await dc.begin_dialog("register")
                await _conversation.save_changes(turn)

    # каждое сообщение
    async def on_message_activity(self, turn: TurnContext):
        dc = await self.dialogs.create_context(turn)
        result = await dc.continue_dialog()

        if result.status == DialogTurnStatus.Empty:
            await dc.begin_dialog("register")

        await _conversation.save_changes(turn)
