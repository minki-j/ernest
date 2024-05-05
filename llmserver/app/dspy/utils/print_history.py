import dspy 

def print_dspy_history(n=1):
    print("---------lm.inspect_history-----------")
    print(dspy.settings.lm.inspect_history(n=n))
    print("LLM: ", dspy.settings.lm)
    print("---------lm.inspect_history-----------")