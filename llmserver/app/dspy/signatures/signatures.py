import dspy

class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")
    print("Class Initialized: GenerateAnswer")


class GenerateSearchQuery(dspy.Signature):
    """Write a simple search query that will help answer a complex question."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    query = dspy.OutputField()


class GenerateChatReply(dspy.Signature):
    """Generate a reply to a chat message."""

    previous_messages = dspy.InputField(desc="previous chat messages")
    user_info = dspy.InputField(desc="user information")
    message = dspy.InputField()
    reply = dspy.OutputField()


class IntentClassifier(dspy.Signature):
    """Classify the given input's intent."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField(desc="the text to be classified")
    options = dspy.InputField(desc="may contain multiple choice options for possible intents")
    intent = dspy.OutputField(desc="the correct option of intent. must be the text not the index or option index.")
    print("Class Initialized: IntentClassifier")

class AssessIntentClassification(dspy.Signature):
    """Assess the intent classification task. Answer succinctly whether the predicted intent is correct. Do not repeat the question."""

    gold_intent = dspy.InputField(desc="the correct intent")
    predicted_intent = dspy.InputField(desc="the predicted intent")
    is_correct = dspy.OutputField(
        desc='''return "true" if gold_intent and pred share the same meaning, "false" if they differ. do not repeat the question.'''
    )
    print("Class Initialized : AssessIntentClassification")
