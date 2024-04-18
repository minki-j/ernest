from modal import enter, method
from app.common import stub, image
from app.dspy.signatures import RAG
# import dspy
# from dspy.teleprompt import BootstrapFewShot

@stub.cls(image=image)
class Compile:
    @enter()
    def run_this_on_container_startup(self):
        import dspy
        self.compile_RAG = None
        self.trainset = None

    # Validation logic: check that the predicted answer is correct.
    # Also check that the retrieved context does actually contain that answer.
    def validate_context_and_answer(example, pred, trace=None):
        answer_EM = dspy.evaluate.answer_exact_match(example, pred)
        answer_PM = dspy.evaluate.answer_passage_match(example, pred)
        return answer_EM and answer_PM

    @method()
    def compile(self, module_name: str):
        print("Downloading dataset...")
        dataset = dspy.datasets.HotPotQA(train_seed=1, train_size=20, eval_seed=2023, dev_size=50, test_size=0)
        self.trainset = [x.with_inputs("question") for x in dataset.train]

        print("Checking module name ", module_name)
        if module_name == "rag":
            # Set up a basic teleprompter, which will compile our RAG program.
            teleprompter = dspy.teleprompt.BootstrapFewShot(metric=self.validate_context_and_answer)

            # Compile!
            compiled_rag = teleprompter.compile(RAG(), trainset=self.trainset)
            return {"message": "Module compiled successfully!"}

    @method()
    def compiled_RAG(self, question: str):
        if self.compile_RAG is None:
            self.compile_RAG = dspy.Predict(RAG)
        return self.compile_RAG(question=question)

# # Load the dataset.
# dataset = HotPotQA(
#     train_seed=1, train_size=20, eval_seed=2023, dev_size=50, test_size=0
# )

# # Tell DSPy that the 'question' field is the input. Any other fields are labels and/or metadata.
# trainset = [x.with_inputs("question") for x in dataset.train]
# devset = [x.with_inputs("question") for x in dataset.dev]
