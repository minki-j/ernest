import dspy

class PurePrompt(dspy.Signature):
    prompt = dspy.InputField()
    output = dspy.OutputField()
    print("Class Initialized: PurePrompt")

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
    """Generate a reply to a chat message"""

    context = dspy.InputField(desc="context")
    conversation = dspy.InputField(desc="converation")
    instruction= dspy.InputField(desc="may contain some instruction to reply in a specific way or about some content")
    ai = dspy.OutputField(desc="reply from the AI")


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


class ChooseNextQuestion(dspy.Signature):
    """Choose the next question to ask. It's better to ask something relevant to the current conversation flow."""

    recent_messages = dspy.InputField(desc="recent messages in the conversation")
    options = dspy.InputField(desc="may contain multiple choice options for possible next questions")
    next_question = dspy.OutputField(desc="the next question to ask")
    print("Class Initialized : ChooseNextQuestion")


class AssessUsefulness(dspy.Signature):
    """Assess the usefulness of the last 3 messages in a conversation."""

    last_messages = dspy.InputField(desc="last 3 messages in the conversation")
    usefulness_score = dspy.OutputField(desc="a score between 0 and 1")
    extraction = dspy.OutputField(desc="a string extracted from the messages")
    print("Class Initialized : AssessUsefulness")


class CheckEnoughAnswerForQuestion(dspy.Signature):
    """Check if the answer is enough for the question."""

    question = dspy.InputField(desc="question")
    answer = dspy.InputField(desc="answer")
    enoughness_score = dspy.OutputField(desc="a score between 0 and 1")
    print("Class Initialized : CheckEnoughAnswerForQuestion")
