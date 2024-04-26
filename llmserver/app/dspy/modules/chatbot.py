import dspy

from app.dspy.signatures.signatures import GenerateChatReply
from app.dspy.utils.initialize_DSPy import initialize_DSPy

class Chatbot(dspy.Module):

    def __init__(self, lm_name="gpt-3.5-turbo"):
        super().__init__()

        initialize_DSPy(lm_name=lm_name)

        self.generate_chat_reply = dspy.Predict(GenerateChatReply, temperature=0.5, )
        print("Class Initialized : Chatbot")

    def forward(self, user_info, previous_messages, message):

        pred = self.generate_chat_reply(
            user_info=user_info,
            previous_messages=previous_messages,
            message=message,
        )
        return dspy.Prediction(reply=pred.reply)
