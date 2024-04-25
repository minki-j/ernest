import dspy

from app.dspy.signatures.signatures import Classifier
from app.dspy.utils.load_compiled_module import load_compiled_module_if_exists


class IntentClassifier(dspy.Module):
    def __init__(self):
        super().__init__()

        load_compiled_module_if_exists(self, "intent_classifier")

        self.generate_chat_reply = dspy.Predict(Classifier)
        print("Class Initialized : IntentClassifier")

    def forward(self, question, options=None, context=None):

        pred = self.generate_chat_reply(
            context=context,
            question=question,
            options=options,
        )

        return dspy.Prediction(reply=pred.answer)
