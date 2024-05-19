import dspy

from app.dspy.lm_clients.llama3_8b import Llama3_8b_Modal_Client

def initialize_DSPy(lm_name="gpt-3.5-turbo", rm_name="colbert"):
    if not dspy.settings.lm or not dspy.settings.rm:
        print("Setting up DSPy configuration...")
        if lm_name == "gpt-3.5-turbo":
            lm = dspy.OpenAI(model="gpt-3.5-turbo")
        elif lm_name == "llama3_8b_on_vllm":
            lm = Llama3_8b_Modal_Client(vllm=True)
        elif lm_name == "llama3_8b":
            lm = Llama3_8b_Modal_Client(vllm=False)

        if rm_name == "colbert":
            rm = dspy.ColBERTv2(url="http://20.102.90.50:2017/wiki17_abstracts")
        dspy.settings.configure(lm=lm, rm=rm)
    else:
        lm = dspy.settings.lm
        rm = dspy.settings.rm
        print("DSPy configuration already set")

    return lm, rm
