import dspy

from app.dspy.signatures.signatures import AssessIntentClassification

# Validation logic: check that the predicted answer is correct.
# Also check that the retrieved context does actually contain that answer.
def validate_context_and_answer(example, pred, trace=None):
    answer_EM = dspy.evaluate.answer_exact_match(example, pred)
    answer_PM = dspy.evaluate.answer_passage_match(example, pred)
    return answer_EM and answer_PM


def validate_intent_classifcation(gold_intent, pred, trace=None):
    bedrock = dspy.Bedrock(region_name="us-west-2")
    anthropic_haiku = dspy.AWSAnthropic(
        bedrock, "anthropic.claude-3-haiku-20240307-v1:0"
    )
    with dspy.context(lm=anthropic_haiku):
        print("validating intent classification. dspy lm: ", dspy.settings.lm)
        pred = AssessIntentClassification(gold_intent=gold_intent, pred=pred)
    return pred.score
