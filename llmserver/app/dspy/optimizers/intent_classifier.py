import os
import pickle

import modal
from modal import enter, method, build, exit, Secret, Volume

import dspy
from dspy.teleprompt import BootstrapFewShot

from app.common import app, image
from app.dspy.modules.intent_classifier import IntentClassifierModule
from app.dspy.utils.initialize_DSPy import initialize_DSPy
from app.dspy.validations.validations import validate_intent_classifcation
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
class CompileIntentClassifier:
    def __init__(self):
        load_dataset(self, "intent_classifier")
        self.trainset_directory_path = os.path.join(vol_path, "dataset")
        self.compiled_module_path = os.path.join(vol_path, "compiled_modules")

    @method()
    def compile(self):

        teleprompter = BootstrapFewShot(
            metric=validate_intent_classifcation,
            max_bootstrapped_demos=4,
            max_labeled_demos=16,
            max_rounds=1,
        )

        initialize_DSPy()

        print("start compiling the module...")
        self.compile_module = teleprompter.compile(
            IntentClassifierModule(), trainset=self.trainset
        )
        print("module compiled successfully!")

        # save the compiled module to disk
        os.makedirs(os.path.dirname(self.compiled_module_path), exist_ok=True)
        self.compile_module.save(
            os.path.join(self.compiled_module_path, "intent_classifier.json")
        )
        vol.commit()
        print("module saved to disk!")

        return {"message": "Module compiled successfully!"}
