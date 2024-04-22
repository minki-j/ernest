import dspy

def initialize_dspy():
    if not dspy.settings.lm or not dspy.settings.rm:
        print("Setting up DSPy configuration...")
        lm = dspy.OpenAI(model="gpt-3.5-turbo")
        rm = dspy.ColBERTv2(url="http://20.102.90.50:2017/wiki17_abstracts")
        dspy.settings.configure(lm=lm, rm=rm)
    else:
        lm = dspy.settings.lm
        rm = dspy.settings.rm
        print("DSPy configuration already set")

    return lm, rm
