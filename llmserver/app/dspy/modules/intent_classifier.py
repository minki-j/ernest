import dspy

from app.dspy.signatures.signatures import IntentClassifier
from app.dspy.utils.load_compiled_module import load_compiled_module_if_exists
from app.dspy.utils.initialize_DSPy import initialize_DSPy


class IntentClassifierModule(dspy.Module):
    def __init__(self, lm_name="gpt-3.5-turbo"):
        super().__init__()

        initialize_DSPy(lm_name=lm_name)
        load_compiled_module_if_exists(self, "intent_classifier")

        self.classify_intent = dspy.Predict(IntentClassifier)
        print("Class Initialized: IntentClassifier")

    def forward(self, question, options="not provided", context="not provided"):

        pred = self.classify_intent(
            context=context,
            question=question,
            options=options,
        )

        return dspy.Prediction(intent=pred.intent)
