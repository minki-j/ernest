import modal
from modal import enter, method, build, exit, Secret
from app.common import stub, image
from app.dspy.signatures import RAG, SimplifiedBaleen
import dspy
from dspy.teleprompt import BootstrapFewShot
from dspy.datasets import HotPotQA
import pickle
import os
from app.utils.dspy_initialize import initialize_dspy


vol = modal.Volume.from_name("survey-buddy")


@stub.cls(
    image=image,
    volumes={"/my_vol": modal.Volume.from_name("survey-buddy")},
    secrets=[
        Secret.from_name("OPENAI_API_KEY"),
        Secret.from_name("Monogo DB connection password"),
        Secret.from_name("my-twilio-secret"),
    ],
)
class Compile:
    def __init__(self):
        self.trainset_path = "/my_vol/dataset/compile_rag/trainset.pickle"
        self.compiled_module_path = "/my_vol"

    @build()
    @enter()
    def build_and_enter(self):
        self.load_compiled_rag()
        self.load_compiled_multi_hop()
        # self.download_dataset()

    def load_compiled_rag(self):
        if os.path.exists(os.path.join(self.compiled_module_path, "rag.json")):
            print("Loading compiled RAG from volume")
            self.compile_RAG = RAG()
            self.compile_RAG.load("/my_vol/rag.json")
        else:
            self.compile_RAG = None

    def load_compiled_multi_hop(self):
        self.compile_multi_hop = None

    def download_dataset(self):
        if os.path.exists(self.trainset_path):
            print("Loading dataset from volume")
            self.trainset = pickle.load(open(self.trainset_path, "rb"))
        else:
            print("Downloading dataset")
            dataset = HotPotQA(
                train_seed=1, train_size=20, eval_seed=2023, dev_size=50, test_size=0
            )

            self.trainset = [x.with_inputs("question") for x in dataset.train]

            # save the trainset to disk
            os.makedirs(os.path.dirname(self.trainset_path), exist_ok=True)
            with open(
                self.trainset_path,
                "wb",
            ) as f:
                pickle.dump(self.trainset, f)
            vol.commit()

    # Validation logic: check that the predicted answer is correct.
    # Also check that the retrieved context does actually contain that answer.
    def validate_context_and_answer(self, example, pred, trace=None):
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

            initialize_dspy()

            print("Starting to compile")
            self.compile_RAG = teleprompter.compile(RAG(), trainset=self.trainset)

        # save the compiled module to disk
        os.makedirs(os.path.dirname(self.compiled_module_path), exist_ok=True)
        print("file in /my_vol: ", os.listdir("/my_vol"))
        self.compile_RAG.save("/my_vol/rag.json")
        vol.commit()

        return {"message": "Module compiled successfully!"}

    @method()
    def compiled_RAG(self, question: str):
        print("Function call on <compiled_RAG>")

        lm, rm = initialize_dspy()

        if self.compile_RAG is None:
            self.compile_RAG = RAG()

        pred = self.compile_RAG(question=question)

        print("lm history: ", lm.inspect_history(1))
        return pred

    @method()
    def multi_hop(self, question: str, max_hops: int):
        lm, rm = initialize_dspy()

        if self.compile_multi_hop is None:
            self.compile_multi_hop = SimplifiedBaleen(max_hops=max_hops)

        pred = self.compile_multi_hop(question=question)

        print("lm history: ", lm.inspect_history(max_hops + 1))

        return pred
