import dspy

from app.dspy.signatures.signatures import (
    GenerateChatReply,
    ChooseNextQuestion,
    AssessUsefulness,
    CheckEnoughAnswerForQuestion,
)
from app.dspy.utils.initialize_DSPy import initialize_DSPy
from app.dspy.modules.intent_classifier import IntentClassifierModule

from app.utils.mongodb import (
    fetch_unasked_questions,
    get_relevant_question_from_message,
)


class Chatbot(dspy.Module):

    def __init__(self, lm_name="gpt-3.5-turbo", enoughness_score_threshold=0.5):
        super().__init__()

        initialize_DSPy(lm_name=lm_name)

        self.enoughness_score_threshold = enoughness_score_threshold

        self.intent_classifier = IntentClassifierModule()
        self.generate_chat_reply = dspy.Predict(GenerateChatReply)
        self.check_usefulness = dspy.Predict(AssessUsefulness)
        self.check_enough_answer_for_question = dspy.Predict(
            CheckEnoughAnswerForQuestion
        )
        self.choose_next_question = dspy.Predict(ChooseNextQuestion)

        print("Class Initialized: Chatbot")

    def forward(self, user_phone_number, chat_data):
        print("chat_data: ", chat_data)

        relevant_question = chat_data["relevant_question"]
        updated_answer = chat_data["updated_answer"]
        ref_message_ids = chat_data["ref_message_ids"]
        unasked_questions = chat_data["unasked_questions"]
        messages = chat_data["messages"]
        context = chat_data["context"]
        enoughness_threshold = chat_data["enoughness_threshold"]

        # check enoughness
        enoughness_score = self.check_enough_answer_for_question(
            question=relevant_question["question"], answer=relevant_question["answer"]
        ).enoughness_score

        # print("enoughness_score: ", enoughness_score)
        # print("---------lm.inspect_history-----------")
        # print(dspy.settings.lm.inspect_history(n=1))
        # print("LLM: ", dspy.settings.lm)
        # print("---------lm.inspect_history-----------")

        if enoughness_score < self.enoughness_score_threshold:
            # ask more questions about the current topic
            print("ask more questions about the current topic")

            pred = self.generate_chat_reply(
                context=context,
                conversation=messages,
                instruction="your reply should be a question about " + relevant_question["question"],
            )

    # context_string = ""
    # for element in context:
    #     for key, value in element.items():
    #         context_string += str(key) + ": " + str(value) + "\n"

    # conversation_string = ""
    # for msg in conversation:
    #     conversation_string += str(msg["role"]) + ": " + str(msg["content"]) + "\n"

    # # check if the relevant question to the user's last answer
    # last_user_message = conversation[-1]["content"]
    # last_bot_message = conversation[-2]["content"]

    # relevant_question = get_relevant_question_from_message(
    #     user_phone_number, last_bot_message
    # )

    # enoughness_score = self.check_enough_answer_for_question(
    #     question=relevant_question["question"], answer=relevant_question["answer"]
    # ).enoughness_score
    # print("enoughness_score: ", enoughness_score)

    # # if no relevant question found, ask more
    # # if threhold is not met, ask more
    # # if both are not met, choose other question
    # if relevant_question and relevant_question["enough_score"] < self.enoughness_score_threshold:
    #     # ask more questions about the current topic
    #     print("ask more questions about the current topic")

    #     pred = self.generate_chat_reply(
    #         context=context_string,
    #         conversation=conversation_string,
    #         instruction="your reply should be a question about " + next_question,
    #     )

    # else:
    #     # choose other question
    #     options = fetch_unasked_questions(user_phone_number)
    #     next_question = self.choose_next_question(
    #         last_messages=[message["content"] for message in conversation],
    #         options=options,
    #     ).next_question

    #     pred = self.generate_chat_reply(
    #         context=context_string,
    #         conversation=conversation_string,
    #         instruction="your reply should be a question about "+ next_question,
    #     )

    # return dspy.Prediction(reply=pred.bot, user_message_id=user_message_id, reply_id=reply_id, updated_answer=updated_answer, enoughness_score=enoughness_score)

    def check_intent(self, message):
        return self.intent_classifier.forward(
            message,
            options="web_search, chat, other",
        ).intent
