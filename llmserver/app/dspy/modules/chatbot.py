import dspy

import json
from datetime import datetime
from bson.objectid import ObjectId

from app.dspy.signatures.signatures import (
    GenerateChatReply,
    ChooseNextQuestion,
    CheckEnoughAnswerForQuestion,
    PurePrompt
)
from app.dspy.utils.initialize_DSPy import initialize_DSPy
from app.dspy.utils.print_history import print_dspy_history


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        # don't include ObjectId and created_at in the json
        if isinstance(o, ObjectId) or o == "created_at":
            return
        return json.JSONEncoder.default(self, o)


class Chatbot(dspy.Module):

    def __init__(self, lm_name="gpt-3.5-turbo", enoughness_threshold=0.8):
        super().__init__()
        initialize_DSPy(lm_name=lm_name)

        self.enoughness_score_threshold = enoughness_threshold

        self.generate_chat_reply = dspy.Predict(GenerateChatReply)
        self.check_enough_answer_for_question = dspy.Predict(CheckEnougcheck_enough_answer_for_questionhAnswerForQuestion)
        self.choose_next_question = dspy.Predict(ChooseNextQuestion)

        print("Class Initialized: Chatbot")

    def forward(self, documents):
        '''
        Flow engineering
        1. if there is no previous conversation or no relevant question
            1.1 pick a question from the list
        2. if a relevant question exists
            2.2 update the answer with user's last message
            2.3 check if the answer is enough
                2.3.1 if not enough, ask more questions about the current topic
                2.3.2 if enough, choose the next question
        '''

        id_of_last_bot_message = None
        for msg in reversed(documents["messages"]):
            if msg["role"] == "ai":
                id_of_last_bot_message = msg["id"]
                break

        relevant_question = None
        relevant_question_idx = None
        if id_of_last_bot_message:
            for idx, question in enumerate(documents["questions"]):
                if id_of_last_bot_message in question["reference_message_ids"]:
                    relevant_question = question
                    relevant_question_idx = idx
                    break

        ask_other_question = True
        if relevant_question:
            # update the answer with the user's last message
            updated_answer = self.update_answer(relevant_question, documents["messages"][-1]["content"])
            for question in documents["questions"]:
                if question["content"] == relevant_question["content"]:
                    relevant_question_idx = idx
                    break

            # check enoughness
            enoughness_score = float(
                self.check_enough_answer_for_question(
                    question=relevant_question["content"],
                    answer=updated_answer,
                ).enoughness_score
            )
            print("enoughness_score: ", enoughness_score)

            # update documents
            documents["questions"][relevant_question_idx]["answer"] = updated_answer
            documents["questions"][relevant_question_idx]["enough"] = enoughness_score

            if enoughness_score < self.enoughness_score_threshold:
                ask_other_question = False

        json_encoder = JSONEncoder()
        next_question = None
        if ask_other_question:
            unasked_questions = []
            for question in documents["questions"]:
                if question["enough"] < self.enoughness_score_threshold:
                    unasked_questions.append(question["content"])
            next_question = self.choose_next_question(
                recent_messages=json_encoder.encode(documents["messages"][-4:]),
                options=" / ".join(unasked_questions),
            ).next_question

            pred = self.generate_chat_reply(
                context=json_encoder.encode(documents["user_info"]),
                conversation=json_encoder.encode(documents["messages"][-4:]),
                instruction="first response to the user's last message and ask a question about the following: " + next_question,
            )
        else:
            pred = self.generate_chat_reply(
                context=json_encoder.encode(documents["user_info"]),
                conversation=json_encoder.encode(documents["messages"][-4:]),
                instruction="The current answer is not enough. Please ask more questions about the current topic.",
            )

        # update documents / add bot's reply
        bot_reply_id = ObjectId()
        documents["messages"].append(
            {
                "id": bot_reply_id,
                "role": "ai",
                "content": pred.ai,
                "created_at": datetime.now().isoformat(),
            }
        )

        # if the bot is asking a next question, change the relevant question id
        if next_question:
            for idx, question in enumerate(documents["questions"]):
                if question["content"].strip() == next_question.strip():
                    relevant_question_idx = idx
                    break

        # update documents / add reference_message_ids
        documents["questions"][relevant_question_idx]["reference_message_ids"].append(bot_reply_id)

        return dspy.Prediction(
            reply=pred.ai,
            new_document=documents,
        )

    def check_intent(self, message):
        return self.intent_classifier.forward(
            message,
            options="web_search, chat, other",
        ).intent

    def update_answer(self, relevant_question, user_message):
        question_content = relevant_question["content"]
        original_answer = relevant_question.get("answer", "")

        prompt = f"""
    Update the answer of the following question based on the user's last message:\n
    ---\n
    Example\n
    \n
    Question: how was the assignments of the course?\n
    Previous Answer: It was too much for me.\n
    User's Last Message: I mean, there were 3 assignment in total every week and it took 3 hours to complete. I think it was too much for me. Also, the deadline was too short. And some of the assignments were too messy and not clearly explained.\n
    Output: The workload was overwhelming with three assignments each week, each requiring three hours to complete and with tight deadlines. Moreover, some of the assignments were disorganized and lacked clear instructions.\n
    ---\n
    Question: {question_content}\n
    Previous Answer: {original_answer or "not answered yet"}\n
    User's Last Message: {user_message}\n
    """

        initialize_DSPy(lm_name="gpt-3.5-turbo")

        pure_prompt = dspy.Predict(PurePrompt)
        updated_answer = pure_prompt(prompt=prompt).output
        return updated_answer
