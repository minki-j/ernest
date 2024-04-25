import os
import pickle

import modal
from modal import enter, method, build, exit, Secret

import dspy
from dspy.teleprompt import BootstrapFewShot

from app.common import app, image
from app.dspy.modules.intent_classifier import IntentClassifier
from app.dspy.utils.initialize_DSPy import initialize_DSPy
from app.dspy.validations.validations import validate_intent_classifcation
from app.dspy.utils.load_dataset import load_dataset


vol = modal.Volume.from_name("survey-buddy")
vol_path = "/my_vol/"


@app.cls(
    image=image,
    volumes={vol_path: modal.Volume.from_name("survey-buddy")},
    secrets=[
        Secret.from_name("OPENAI_API_KEY"),
        Secret.from_name("my-anthropic-secret"),
        Secret.from_name("Monogo DB connection password"),
    ],
)
class CompileIntentClassifier:
    def __init__(self):
        load_dataset(self, "intent_classifier")
        self.trainset_directory_path = os.path.join(vol_path, "/dataset/")
        self.compiled_module_path = os.path.join(vol_path, "/compiled_modules/")

    @method()
    def compile(self):

        
        teleprompter = BootstrapFewShot(
            metric=validate_intent_classifcation
        )

        initialize_DSPy()

        print("Starting to compile")
        self.compile_module = teleprompter.compile(
            IntentClassifier(), trainset=self.trainset
        )

        # save the compiled module to disk
        os.makedirs(os.path.dirname(self.compiled_module_path), exist_ok=True)
        self.compile_module.save(f"{self.compiled_module_path}/intent_classifier.json")
        vol.commit()

        return {"message": "Module compiled successfully!"}
