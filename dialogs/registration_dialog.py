from botbuilder.dialogs import (
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    PromptOptions,
    TextPrompt,
)
from botbuilder.core import MessageFactory
from services.db import save_user


class RegistrationDialog(WaterfallDialog):
    """8-шаговый waterfall-диалог регистрации."""

    def __init__(self) -> None:
        super().__init__("register")

        # регистрируем шаги
        self.add_step(self.ask_first)
        self.add_step(self.ask_last)
        self.add_step(self.ask_phone)
        self.add_step(self.ask_email)
        self.add_step(self.ask_country)
        self.add_step(self.ask_city)
        self.add_step(self.ask_zip)
        self.add_step(self.finish)

    # ───────── helpers ─────────
    @staticmethod
    def _prompt(text: str) -> PromptOptions:
        """Упрощает вызов step.prompt: возвращает PromptOptions."""
        return PromptOptions(prompt=MessageFactory.text(text))

    # ───────── waterfall-шаги ─────────
    async def ask_first(self, step: WaterfallStepContext) -> DialogTurnResult:
        return await step.prompt("text", self._prompt("Hi! 👋 What’s your **first name**?"))

    async def ask_last(self, step):
        step.values["first"] = step.result.strip()
        return await step.prompt("text", self._prompt("Great, and your **last name**?"))

    async def ask_phone(self, step):
        step.values["last"] = step.result.strip()
        return await step.prompt("text", self._prompt("📱 Could I have your phone number?"))

    async def ask_email(self, step):
        step.values["phone"] = step.result.strip()
        return await step.prompt("text", self._prompt("✉️ Your e-mail address?"))

    async def ask_country(self, step):
        step.values["email"] = step.result.strip()
        return await step.prompt("text", self._prompt("🌍 Country of residence?"))

    async def ask_city(self, step):
        step.values["country"] = step.result.strip()
        return await step.prompt("text", self._prompt("🏙️ City?"))

    async def ask_zip(self, step):
        step.values["city"] = step.result.strip()
        return await step.prompt("text", self._prompt("ZIP / postal code?"))

    async def finish(self, step):
        step.values["zip"] = step.result.strip()

        # сохраняем ответы (если настроен SQL)
        save_user(step.values)

        await step.context.send_activity(
            f"Thanks **{step.values['first']}** – you’re all set! ✅"
        )
        return await step.end_dialog()

