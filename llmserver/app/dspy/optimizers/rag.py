import os

from modal import Secret, Volume, method, enter, build, exit

import dspy
from dspy.teleprompt import BootstrapFewShot

from app.common import app, image
from app.dspy.modules.rag import RAG
from app.dspy.utils.initialize_DSPy import initialize_DSPy
from app.dspy.validations.validations import validate_context_and_answer
from app.dspy.utils.load_dataset import load_dataset


vol = Volume.from_name("survey-buddy")
vol_path = "/my_vol/"


@app.cls(
    image=image,
    volumes={vol_path: Volume.from_name("survey-buddy")},
    secrets=[
        Secret.from_name("OPENAI_API_KEY"),
        Secret.from_name("my-anthropic-secret"),
        Secret.from_name("Monogo DB connection password"),
    ],
)
class CompileRag:
    def __init__(self):
        self.trainset = load_dataset(self, "rag")
        self.trainset_directory_path = os.path.join(vol_path, "/dataset/")
        self.compiled_module_path = os.path.join(vol_path, "/compiled_modules")

    @method()
    def compile(self, module_name: str):
        print("Checking module name ", module_name)
        if module_name == "rag":
            # Set up a basic teleprompter, which will compile our RAG program.
            teleprompter = BootstrapFewShot(
                metric=validate_context_and_answer
            )

            initialize_DSPy()

            print("Starting to compile")
            self.compile_module = teleprompter.compile(RAG(), trainset=self.trainset)

        # save the compiled module to disk
        os.makedirs(os.path.dirname(self.compiled_module_path), exist_ok=True)
        self.compile_module.save(f"{self.compiled_module_path}/{module_name}.json")
        vol.commit()

        return {"message": "Module compiled successfully!"}
