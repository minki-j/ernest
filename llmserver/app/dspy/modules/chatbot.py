import dspy

from app.dspy.signatures.signatures import (
    GenerateChatReply,
    ChooseNextQuestion,
    AssessUsefulness,
    CheckEnoughAnswerForQuestion,
)
from app.dspy.utils.initialize_DSPy import initialize_DSPy
from app.dspy.modules.intent_classifier import IntentClassifierModule
from app.dspy.utils.print_history import print_dspy_history

from app.utils.mongodb import (
    fetch_unasked_questions,
    get_relevant_question_from_message,
)


class Chatbot(dspy.Module):

    def __init__(self, lm_name="gpt-3.5-turbo", enoughness_score_threshold=0.5):
        super().__init__()

        initialize_DSPy(lm_name=lm_name)

        self.enoughness_score_threshold = enoughness_score_threshold

        # self.intent_classifier = IntentClassifierModule()
        self.generate_chat_reply = dspy.Predict(GenerateChatReply)
        self.check_usefulness = dspy.Predict(AssessUsefulness)
        self.check_enough_answer_for_question = dspy.Predict(
            CheckEnoughAnswerForQuestion
        )
        self.choose_next_question = dspy.Predict(ChooseNextQuestion)

        print("Class Initialized: Chatbot")

    def forward(self, chat_data):

        relevant_question = chat_data["relevant_question"]
        updated_answer = chat_data["updated_answer"]
        ref_message_ids = chat_data["ref_message_ids"]
        unasked_questions = chat_data["unasked_questions"]
        messages = chat_data["messages"]
        context = chat_data["context"]
        enoughness_threshold = chat_data["enoughness_threshold"]

        conversation_string = ""
        for idx, msg in enumerate(messages):
            conversation_string += str(msg["role"]) + ": " + str(msg["content"]) + "\n"
            idx += 1
            if idx == 4:
                break

        context_string = ""
        for key, value in context.items():
            context_string += str(key) + ": " + str(value) + "\n"

        enoughness_score = None
        if relevant_question:
            # check enoughness
            enoughness_score = float(
                self.check_enough_answer_for_question(
                    question=relevant_question["question"],
                    answer=relevant_question["answer"],
                ).enoughness_score
            )
            # print_dspy_history(1)

            if enoughness_score < enoughness_threshold:
                # ask more questions about the current topic
                print("ask more questions about the current topic")

                context_string += "current topic: " + relevant_question["question"]
                context_string += "current answer: " + updated_answer

                pred = self.generate_chat_reply(
                    context=context_string,
                    conversation=conversation_string,
                    instruction="The current answer is not enough. Please ask more questions about the current topic.",
                )
                return dspy.Prediction(
                    reply=pred.bot, enoughness_score=enoughness_score, next_question=None
                )

        # choose other question if there is no relevant question or the answer is enough
        next_question = self.choose_next_question(
            recent_messages=conversation_string,
            options=" / ".join([question["question"] for question in unasked_questions]),
        ).next_question


        # print_dspy_history(1)

        pred = self.generate_chat_reply(
            context=context_string,
            conversation=conversation_string,
            instruction="first response to the user's last message and ask a question about the following: " + next_question,
        )
        # print_dspy_history(1)

        return dspy.Prediction(
            reply=pred.bot,
            enoughness_score=enoughness_score,
            next_question=next_question,
        )

    def check_intent(self, message):
        return self.intent_classifier.forward(
            message,
            options="web_search, chat, other",
        ).intent
