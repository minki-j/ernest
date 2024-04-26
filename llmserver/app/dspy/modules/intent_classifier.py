import dspy

from app.dspy.signatures.signatures import IntentClassifier
from app.dspy.utils.load_compiled_module import load_compiled_module_if_exists


class IntentClassifierModule(dspy.Module):
    def __init__(self):
        super().__init__()

        load_compiled_module_if_exists(self, "intent_classifier")

        self.classify_intent = dspy.Predict(IntentClassifier)
        print("Class Initialized : IntentClassifier")

    def forward(self, question, options="not provided", context="not provided"):

        pred = self.classify_intent(
            context=context,
            question=question,
            options=options,
        )

        # print("---------lm.inspect_history-----------")
        # print(dspy.settings.lm.inspect_history(n=1))
        # print("---------lm.inspect_history-----------")

        return dspy.Prediction(intent=pred.intent)
