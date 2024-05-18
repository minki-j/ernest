from typing import Literal

from app.langchain.common import Documents

def is_start_of_conversation(Documents: Documents):
    print("==>> is_start_of_conversation")

    if len(Documents["review"]["messages"]) < 2:
        return "generate_reply"
    else:
        return "decide_next_step"

def decide_to_pick_new_question(
    Documents: Documents,
) -> Literal["generate_answer_with_new_msg", "decide_next_question"]:
    print("==>> decide_to_pick_new_question")
    # becareful to not use boolean comparison here since index 0 is False
    if Documents["ephemeral"]["relevant_question_idx"] is None:
        print("-> decide_next_question")
        return "decide_next_question"
    else:
        print("-> generate_answer_with_new_msg -> check_enoughness_score")
        return "generate_answer_with_new_msg"


def decide_enoughness_threshold(
    Documents: Documents,
) -> Literal["decide_next_question", "generate_new_q_for_current_topic"]:
    print("==>> decide_enoughness_threshold")
    current_topic_idx = Documents["ephemeral"]["current_topic_idx"]
    relevant_question_idx = Documents["ephemeral"]["relevant_question_idx"]
    enoughness_score = Documents["topics"][current_topic_idx]["questions"][
        relevant_question_idx
    ]["enough"]

    if enoughness_score < Documents["ephemeral"]["enoughness_threshold"]:
        return "generate_new_q_for_current_topic"
    else:
        return "decide_next_question"


def is_next_Q(Documents: Documents) -> Literal["generate_answer_with_new_msg", "decide_next_question"]:
    print("==>> is_next_Q")

    current_topic_idx = Documents["ephemeral"]["current_topic_idx"]

    questions = Documents["topics"][current_topic_idx]["questions"]

    questions_lower_than_threshold = [
        q for q in questions if q["enough"] < Documents["ephemeral"]["enoughness_threshold"]
    ]

    if len(questions_lower_than_threshold) == 0:
        return "fork2"
    else:
        return "pick_next_Q"
