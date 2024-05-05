import modal
import os
import time

from app.common import app

VOL_DIR = "/my_vol"
MODEL_DIR = "/model"
MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
GPU_CONFIG = modal.gpu.A10G()


def download_model_to_image(model_dir, model_name):
    print("function download_model_to_image starts")
    from huggingface_hub import snapshot_download
    from transformers.utils import move_cache

    os.makedirs(model_dir, exist_ok=True)

    snapshot_download(
        model_name,
        token=os.environ["HF_TOKEN"],
        local_dir=model_dir,
        ignore_patterns=["*.pt", "*.bin", "*.gguf"],  # Using safetensors
    )
    move_cache()
    print("function download_model_to_image ends")


image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "torch==2.1.2",
        "transformers==4.39.3",
        "ray==2.10.0",
        "huggingface_hub==0.19.4",
        "hf-transfer==0.1.4",
        "accelerate",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    .run_function(
        download_model_to_image,
        timeout=60 * 20,
        kwargs={
            "model_dir": os.path.join(VOL_DIR, MODEL_DIR),
            "model_name": MODEL_NAME,
        },
        secrets=[modal.Secret.from_name("huggingface-secret")],
    )
)
with image.imports():
    import transformers
    import torch

@app.cls(
    image=image,
    gpu=GPU_CONFIG,
    secrets=[modal.Secret.from_name("huggingface-secret")],
)
class Llama3_8B:
    def __init__(self):
        print("Class initialized: Llama3_8B_on_VLLM")
        pass

    @modal.enter()
    def load(self):
        self.llm = transformers.pipeline(
            "text-generation",
            model=MODEL_DIR,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
        )
        print("Model loaded: Llama3_8B")

    @modal.method()
    def generate(self, prompt):

        terminators = [
            self.llm.tokenizer.eos_token_id,
            self.llm.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        start = time.monotonic_ns()
        outputs = self.llm(
            prompt,
            max_new_tokens=100,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
        )
        duration_s = (time.monotonic_ns() - start) / 1e9


        COLOR = {
            "HEADER": "\033[95m",
            "BLUE": "\033[94m",
            "GREEN": "\033[92m",
            "RED": "\033[91m",
            "ENDC": "\033[0m",
        }

        num_tokens = "100"
        print(
            f"{COLOR['HEADER']}Generated {num_tokens} tokens from {MODEL_NAME} in {duration_s:.3f} seconds on {GPU_CONFIG} using HuggingFace Pipeline.{COLOR['ENDC']}"
        )

        return [outputs[0][0]["generated_text"][len(prompt[0]) :]]

    @modal.exit()
    def stop_engine(self):
        if GPU_CONFIG.count > 1:
            import ray

            ray.shutdown()
