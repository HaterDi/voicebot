# dialogs/registration_dialog.py
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    TextPrompt,
    PromptOptions,
)
from botbuilder.core import MessageFactory
from services.db import save_user
from services.speech_handler import speak


class RegistrationDialog(ComponentDialog):
    def __init__(self):
        super().__init__("register")

        # порядок вопросов
        self.fields = [
            ("first_name", "What is your first name?"),
            ("last_name", "What is your last name?"),
            ("phone", "What is your phone number?"),
            ("email", "What is your email address?"),
            ("country", "Which country do you live in?"),
            ("city", "Which city?"),
            ("zip", "What is your ZIP code?"),
        ]

        # единственный текстовый prompt
        self.add_dialog(TextPrompt("text"))

        # динамически строим шаги: ask / confirm / process за поле
        steps = []
        for idx, (key, question) in enumerate(self.fields):
            steps.append(self._make_ask(idx, key, question))
            steps.append(self._make_confirm(idx, key))
            steps.append(self._make_process_confirm(idx, key))
        steps.append(self._finish)

        self.add_dialog(WaterfallDialog("flow", steps))
        self.initial_dialog_id = "flow"

    # ---------- фабрики шагов ----------
    def _make_ask(self, idx, key, question):
        async def step(step_ctx: WaterfallStepContext):
            # сохраняем индекс текущего вопроса
            step_ctx.values["idx"] = idx
            step_ctx.values["key"] = key
            speak(question)
            return await step_ctx.prompt(
                "text",
                PromptOptions(prompt=MessageFactory.text(question)),
            )
        return step

    def _make_confirm(self, idx, key):
        async def step(step_ctx: WaterfallStepContext):
            # сохранили введённое значение временно
            step_ctx.values["candidate"] = step_ctx.result.strip()
            confirm_q = f'You said: "{step_ctx.values["candidate"]}". Is that correct? (yes / no)'
            speak(confirm_q)
            return await step_ctx.prompt(
                "text",
                PromptOptions(prompt=MessageFactory.text(confirm_q)),
            )
        return step

    def _make_process_confirm(self, idx, key):
        async def step(step_ctx: WaterfallStepContext):
            answer = step_ctx.result.strip().lower()
            if answer != "yes":
                # повторяем тот же вопрос
                return await step_ctx.replace_dialog("register", {"restart_from": idx})

            # подтверждено ‒ сохраняем
            step_ctx.values[key] = step_ctx.values["candidate"]

            # если ещё есть поля ‒ двигаемся к следующему
            if idx + 1 < len(self.fields):
                return await step_ctx.next(None)  # перейдём к ask следующего поля

            # иначе ‒ к финишу
            return await step_ctx.next("done")
        return step

    # ---------- финальный шаг ----------
    async def _finish(self, step_ctx: WaterfallStepContext):
        # данный шаг вызывается один раз, когда получим "done"
        save_user(step_ctx.values)
        speak("Thank you for registering!")
        await step_ctx.context.send_activity("✅ Thank you for registering!")
        return await step_ctx.end_dialog()
