import modal
from modal import enter, method, build, exit
from app.common import stub, image
from app.dspy.signatures import RAG
import dspy
from dspy.teleprompt import BootstrapFewShot
from dspy.datasets import HotPotQA
import pickle
import os

vol = modal.Volume.from_name("survey-buddy")

@stub.cls(image=image, volumes={"/my_vol": modal.Volume.from_name("survey-buddy")})
class Compile:
    def __init__(self):
        self.compile_RAG = None
        self.trainset_path = "/my_vol/dataset/compile_rag/trainset.pickle"

    @build()
    @enter()
    def download_dataset(self):
        if os.path.exists(self.trainset_path):
            print("Loading dataset from volume")
            self.trainset = pickle.load(
                open(self.trainset_path, "rb")
            )
        else:
            print("Downloading dataset")
            dataset = HotPotQA(
                train_seed=1, train_size=20, eval_seed=2023, dev_size=50, test_size=0
            )

            self.trainset = [x.with_inputs("question") for x in dataset.train]

            # save the trainset to disk
            os.makedirs(os.path.dirname(self.trainset_path), exist_ok=True)
            with open(self.trainset_path, "wb", ) as f:
                pickle.dump(self.trainset, f)
            vol.commit()

    # Validation logic: check that the predicted answer is correct.
    # Also check that the retrieved context does actually contain that answer.
    def validate_context_and_answer(example, pred, trace=None):
        answer_EM = dspy.evaluate.answer_exact_match(example, pred)
        answer_PM = dspy.evaluate.answer_passage_match(example, pred)
        return answer_EM and answer_PM

    @method()
    def compile(self, module_name: str):
        print("Checking module name ", module_name)
        if module_name == "rag":
            # Set up a basic teleprompter, which will compile our RAG program.
            teleprompter = dspy.teleprompt.BootstrapFewShot(
                metric=self.validate_context_and_answer
            )
            
            print("RM: ", dspy.settings.rm)

            self.compile_RAG = teleprompter.compile(RAG(), trainset=self.trainset)
            return {"message": "Module compiled successfully!"}

    @method()
    def compiled_RAG(self, question: str):
        if self.compile_RAG is None:
            self.compile_RAG = dspy.Predict(RAG)
        return self.compile_RAG(question=question)
