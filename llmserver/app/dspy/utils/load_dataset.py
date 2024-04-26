import os
import pickle

from modal import Volume

from app.common import app, image

from dspy.datasets import HotPotQA
from dspy import Example

from datasets import load_dataset as hf_load_dataset


vol = Volume.from_name("survey-buddy")
vol_path = "/my_vol/"

app.function(
    image=image,
    volumes={vol_path: Volume.from_name("survey-buddy")},
)


def load_dataset(self, dataset_name):
    print("Loading dataset for ", dataset_name)

    dataset_directory_path = "/my_vol/dataset"
    trainset_path = os.path.join(dataset_directory_path, dataset_name)

    if os.path.exists(trainset_path):
        self.trainset = pickle.load(open(trainset_path, "rb"))
        print("Loaded dataset from volume")
    else:
        print("Downloading dataset")
        self.trainset = fetch_dataset(dataset_name)

        # save the trainset to disk
        os.makedirs(os.path.dirname(dataset_directory_path), exist_ok=True)
        with open(
            trainset_path,
            "wb",
        ) as f:
            pickle.dump(self.trainset, f)
        vol.commit()


def fetch_dataset(dataset_name):
    print("Fetching dataset", dataset_name)
    if dataset_name == "intent_classifier":
        dataset = hf_load_dataset("Bhuvaneshwari/intent_classification")

        #convert the key value of "text" to "question"
        dataset = dataset.map(lambda x: {"question": x["text"]})
        dataset = dataset.remove_columns(["text"])

        # convert the dataset to a list of Example objects from dspy
        trainset = [Example(base=x) for x in list(dataset["train"])]
        return [x.with_inputs("question") for x in trainset]

    elif dataset_name == "rag":
        dataset = HotPotQA(
            train_seed=1, train_size=20, eval_seed=2023, dev_size=50, test_size=0
        )

        return [x.with_inputs("question") for x in dataset.train]
