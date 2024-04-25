import dspy
from app.dspy.utils.initialize_DSPy import initialize_DSPy


class BaseDSPyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        lm, rm = initialize_DSPy()
        print("Class Initialized: BaseDSPyModule")
