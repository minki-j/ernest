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


class Classifier(dspy.Signature):
    """Classify the given input."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField(desc="the text to be classified")
    options = dspy.InputField(desc="multiple choice options")
    answer = dspy.OutputField(desc="the correct option")
    print("Class Initialized: Classifier")

class AssessIntentClassification(dspy.Signature):
    """Assess the intent classification task."""

    gold_intent = dspy.InputField(desc="the correct intent")
    pred = dspy.InputField(desc="the predicted intent")
    score = dspy.OutputField(desc="the score of the prediction (0 or 1)")
    print("Class Initialized : AssessIntentClassification")