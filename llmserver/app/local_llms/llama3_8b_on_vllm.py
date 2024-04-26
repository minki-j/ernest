import modal
import os
import time

VOL_DIR = "/my_vol"
MODEL_DIR = "/model"
MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
GPU_CONFIG = modal.gpu.H100(count=1)


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

app = modal.App(f"{MODEL_NAME}-vllm", image=image)

with image.imports():
    import vllm


@app.cls(
    gpu=GPU_CONFIG,
    secrets=[modal.Secret.from_name("huggingface-secret")],
)
class Llama3_8B_on_VLLM:
    def __init__(self):
        print("Class initialized: Llama3_8B_on_VLLM")
        pass

    @modal.enter()
    def load(self):
        print("load llama3 8b model")
        self.template = "start_of_turn>user\n{user}<end_of_turn>\n<start_of_turn>model"

        # Load the model. Some models, like MPT, may require `trust_remote_code=true`.
        self.llm = vllm.LLM(
            MODEL_DIR,
            enforce_eager=True,  # skip graph capturing for faster cold starts
            tensor_parallel_size=GPU_CONFIG.count,
        )
        print("Model loaded: Llama3_8B_on_VLLM")

    @modal.method()
    def generate(self, user_questions):
        prompts = [self.template.format(user=q) for q in user_questions]

        sampling_params = vllm.SamplingParams(
            temperature=0.75,
            top_p=0.99,
            max_tokens=256,
            presence_penalty=1.15,
        )
        start = time.monotonic_ns()
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
            print(
                f"{COLOR['HEADER']}{COLOR['GREEN']}{output.prompt}",
                f"\n{COLOR['BLUE']}{output.outputs[0].text}",
                "\n\n",
                sep=COLOR["ENDC"],
            )
            time.sleep(0.01)
        print(
            f"{COLOR['HEADER']}{COLOR['GREEN']}Generated {num_tokens} tokens from {MODEL_NAME} in {duration_s:.1f} seconds,"
            f" throughput = {num_tokens / duration_s:.0f} tokens/second on {GPU_CONFIG}.{COLOR['ENDC']}"
        )

        return [output.outputs[0].text for output in result]

    @modal.exit()
    def stop_engine(self):
        if GPU_CONFIG.count > 1:
            import ray

            ray.shutdown()


# @app.local_entrypoint()
# def main():
#     questions = [
#         "Implement a Python function to compute the Fibonacci numbers.",
#         "What is the fable involving a fox and grapes?",
#         "What were the major contributing factors to the fall of the Roman Empire?",
#         "Describe the city of the future, considering advances in technology, environmental changes, and societal shifts.",
#         "What is the product of 9 and 8?",
#         "Who was Emperor Norton I, and what was his significance in San Francisco's history?",
#     ]
#     model = Model()
#     model.generate.remote(questions)
