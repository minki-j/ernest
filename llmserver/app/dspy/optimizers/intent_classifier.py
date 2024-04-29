import os
import pickle

import modal
from modal import enter, method, build, exit, Secret, Volume

import dspy
from dspy.teleprompt import BootstrapFewShot, BootstrapFinetune

from app.common import app, image
from app.dspy.modules.intent_classifier import IntentClassifierModule
from app.dspy.utils.initialize_DSPy import initialize_DSPy
from app.dspy.validations.validations import validate_intent_classifcation
from app.dspy.utils.load_dataset import load_dataset


vol = Volume.from_name("survey-buddy")
VOL_DIR = "/my_vol"


@app.cls(
    image=image,
    volumes={VOL_DIR: Volume.from_name("survey-buddy")},
    secrets=[
        # Secret.from_name("OPENAI_API_KEY"),
        # Secret.from_name("my-anthropic-secret"),
        Secret.from_name("Monogo DB connection password"),
    ],
)
class CompileIntentClassifier:
    def __init__(self, lm_name="gpt-3.5-turbo"):
        load_dataset(self, "intent_classifier")
        self.trainset_directory_path = os.path.join(VOL_DIR, "dataset")
        self.compiled_module_path = os.path.join(VOL_DIR, "compiled_modules")
        self.lm_name = lm_name

    @method()
    def compile(self):

        teleprompter = BootstrapFewShot(
            metric=validate_intent_classifcation,
            max_bootstrapped_demos=4,
            max_labeled_demos=16,
            max_rounds=1,
        )

        initialize_DSPy(lm_name=self.lm_name)

        print("start compiling the module...")
        self.compile_module = teleprompter.compile(
            IntentClassifierModule(), trainset=self.trainset[:10]
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

    @method()
    def compile_t5(self):
        config = dict(target='t5-large', epochs=1, bf16=True, bsize=6, accumsteps=2, lr=5e-5)

        llama_intent_classifier = IntentClassifierModule(lm_name="llama3_8b_on_vllm")

        tp = BootstrapFinetune(metric=None)
        t5_program = tp.compile(
            IntentClassifierModule(),
            teacher=llama_intent_classifier,
            trainset=self.trainset[:100],
            **config
        )
        
        try:
            t5_program.save(os.path.join(self.compiled_module_path, "intent_classifier_t5"))
        except Exception as e:
            print(f"Error saving T5 model: {e}")
            print("model not saved")

        return {"message": "T5 compiled successfully!"}
