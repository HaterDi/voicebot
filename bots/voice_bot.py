# bots/voice_bot.py
from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    MemoryStorage,
    ConversationState,
)
from botbuilder.dialogs import (
    DialogSet,
    DialogTurnStatus,
    TextPrompt,
)

from dialogs.registration_dialog import RegistrationDialog
from services.speech_handler import speak
from services.db import get_all_users

# ──────────────────────────────
# Глобальное состояние бота
# ──────────────────────────────
_memory           = MemoryStorage()
_conversation     = ConversationState(_memory)
DIALOG_STATE_PROP = "dialog_state"


class VoiceBot(ActivityHandler):
    def __init__(self):
        # регистрируем DialogSet
        self.dialog_state = _conversation.create_property(DIALOG_STATE_PROP)
        self.dialogs = DialogSet(self.dialog_state)

        self.dialogs.add(TextPrompt("text"))
        self.dialogs.add(RegistrationDialog())

    # ───── пользователь зашёл в чат ─────
    async def on_members_added_activity(self, members_added, turn: TurnContext):
        for member in members_added:
            if member.id != turn.activity.recipient.id:
                greeting = "Hello! 👋 I'm your registration bot — let's get started!"
                await turn.send_activity(greeting)
                speak(greeting)

                dc = await self.dialogs.create_context(turn)
                await dc.begin_dialog("register")
                await _conversation.save_changes(turn)

    # ───── входящее сообщение ─────
    async def on_message_activity(self, turn: TurnContext):
        text = (turn.activity.text or "").strip().lower()

        # ─── админ-команда show data ───
        if text == "show data":
            rows = get_all_users()
            if not rows:
                await turn.send_activity("No registrations yet.")
            else:
                for r in rows:
                    await turn.send_activity(
                        f"{r[0]} {r[1]} | {r[2]} | {r[3]} | {r[4]}, {r[5]}, {r[6]}"
                    )
            return  # не продолжаем диалог

        # ─── продолжаем / начинаем диалог ───
        dc     = await self.dialogs.create_context(turn)
        result = await dc.continue_dialog()

        if result.status == DialogTurnStatus.Empty:
            await dc.begin_dialog("register")

        await _conversation.save_