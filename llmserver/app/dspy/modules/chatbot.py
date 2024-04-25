import dspy

from app.dspy.signatures.signatures import GenerateChatReply

class Chatbot(dspy.Module):
    def __init__(self):
        super().__init__()

        self.generate_chat_reply = dspy.Predict(GenerateChatReply)
        print("Class Initialized : Chatbot")

    def forward(self, user_info, previous_messages, message):

        pred = self.generate_chat_reply(
            user_info=user_info,
            previous_messages=previous_messages,
            message=message,
        )
        return dspy.Prediction(reply=pred.reply)
