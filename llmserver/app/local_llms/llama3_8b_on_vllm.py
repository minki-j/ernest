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
        "vllm==0.4.0.post1",
        "torch==2.1.2",
        "transformers==4.39.3",
        "ray==2.10.0",
        "huggingface_hub==0.19.4",
        "hf-transfer==0.1.4",
        # "flash-attn==2.5.8",
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
    import vllm


@app.cls(
    image=image,
    gpu=GPU_CONFIG,
    secrets=[modal.Secret.from_name("huggingface-secret")],
)
class Llama3_8B_on_VLLM:
    def __init__(self):
        print("Class initialized: Llama3_8B_on_VLLM")
        pass

    @modal.enter()
    def load(self):
        self.template = "<start_of_turn>user\n{user}<end_of_turn>\n<start_of_turn>model"

        # Load the model. Some models, like MPT, may require `trust_remote_code=true`.
        self.llm = vllm.LLM(
            MODEL_DIR,
            enforce_eager=True,  # skip graph capturing for faster cold starts
            tensor_parallel_size=GPU_CONFIG.count,
        )
        print("Model loaded: Llama3_8B_on_VLLM")

    @modal.method()
    def generate(self, user_questions, use_template=False):
        if use_template:
            prompts = [self.template.format(user=q) for q in user_questions]
        else:
            prompts = user_questions

        sampling_params = vllm.SamplingParams(
            temperature=1,
            top_p=0.99,
            max_tokens=100,
            presence_penalty=1.15,
        )
        start = time.monotonic_ns()
        print("prompt:\n", prompts[0])
        result = self.llm.generate(prompts, sampling_params)
        duration_s = (time.monotonic_ns() - start) / 1e9
        num_tokens = 0

        COLOR = {
            "HEADER": "\033[95m",
            "BLUE": "\033[94m",
            "GREEN": "\033[92m",
            "RED": "\033[91m",
            "ENDC": "\033[0m",
        }

        for output in result:
            num_tokens += len(output.outputs[0].token_ids)
            # print(
            #     f"{COLOR['HEADER']}{COLOR['GREEN']}{output.prompt}",
            #     f"\n{COLOR['BLUE']}{output.outputs[0].text}",
            #     "\n\n",
            #     sep=COLOR["ENDC"],
            # )
            time.sleep(0.01)
        print(
            f"{COLOR['HEADER']}Generated {num_tokens} tokens from {MODEL_NAME} in {duration_s:.3f} seconds on {GPU_CONFIG}.{COLOR['ENDC']}"
        )

        return [output.outputs[0].text for output in result]

    @modal.exit()
    def stop_engine(self):
        if GPU_CONFIG.count > 1:
            import ray

            ray.shutdown()
