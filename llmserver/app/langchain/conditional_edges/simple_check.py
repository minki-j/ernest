from typing import Literal

from app.langchain.states.document_state import DocumentState


def decide_to_pick_new_question(
    documentState: DocumentState,
) -> Literal["generate_answer_with_new_msg", "decide_next_question"]:
    print("==>> decide_to_pick_new_question")
    # becareful to not use boolean comparison here since index 0 is False
    if documentState["ephemeral"]["relevant_question_idx"] is None:
        print("-> decide_next_question")
        return "decide_next_question"
    else:
        print("-> generate_answer_with_new_msg -> check_enoughness_score")
        return "generate_answer_with_new_msg"


def decide_enoughness_threshold(
    documentState: DocumentState,
) -> Literal["decide_next_question", "generate_new_q_for_current_topic"]:
    print("==>> decide_enoughness_threshold")
    current_topic_idx = documentState["ephemeral"]["current_topic_idx"]
    relevant_question_idx = documentState["ephemeral"]["relevant_question_idx"]
    enoughness_score = documentState["topics"][current_topic_idx]["questions"][
        relevant_question_idx
    ]["enough"]

    if enoughness_score < documentState["ephemeral"]["enoughness_threshold"]:
        return "generate_new_q_for_current_topic"
    else:
        return "decide_next_question"


def is_next_Q(documentState: DocumentState) -> Literal["generate_answer_with_new_msg", "decide_next_question"]:
    print("==>> is_next_Q")

    current_topic_idx = documentState["ephemeral"]["current_topic_idx"]

    questions = documentState["topics"][current_topic_idx]["questions"]

    questions_lower_than_threshold = [
        q for q in questions if q["enough"] < documentState["ephemeral"]["enoughness_threshold"]
    ]

    if len(questions_lower_than_threshold) == 0:
        return "fork2"
    else:
        return "pick_next_Q"
