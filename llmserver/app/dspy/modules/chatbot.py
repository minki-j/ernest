import dspy

from app.dspy.signatures.signatures import GenerateChatReply
from app.dspy.utils.initialize_DSPy import initialize_DSPy
from app.dspy.modules.intent_classifier import IntentClassifierModule


class Chatbot(dspy.Module):

    def __init__(self, lm_name="gpt-3.5-turbo"):
        super().__init__()

        initialize_DSPy(lm_name=lm_name)

        self.intent_classifier = IntentClassifierModule()
        self.generate_chat_reply = dspy.Predict(GenerateChatReply)
        print("Class Initialized: Chatbot")

    def forward(self, context, conversation):

        intent = self.check_intent(conversation[-1]["content"])

        if intent == "web_search":
            return dspy.Prediction(
                reply="I am not able to search the web right now. Please ask me something else."
            )

        context_string = ""
        for element in context:
            for key, value in element.items():
                context_string += str(key) + ": " + str(value) + "\n"

        conversation_string = ""
        for msg in conversation:
            conversation_string += str(msg["role"]) + ": " + str(msg["content"]) + "\n"

        pred = self.generate_chat_reply(
            context=context_string,
            conversation=conversation_string,
        )

        return dspy.Prediction(reply=pred.bot)

    def check_intent(self, message):
        return self.intent_classifier.forward(
            message,
            options="web_search, chat, other",
        ).intent
