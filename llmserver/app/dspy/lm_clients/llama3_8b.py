import requests

from dsp import LM

import modal
from app.common import app


class Llama3_8b_Modal_Client(LM):

    def __init__(self, vllm=False):
        self.provider = "default"
        self.history = []

        self.kwargs = {"temperature": 0.7}
        self.vllm = vllm

    def basic_request(self, prompt: str, **kwargs):
        headers = {"content-type": "application/json"}
        running_on_ephemeral = True
        base_url = (
            f"https://jung0072--survey-buddy-fastapi-asgi{"-dev" if running_on_ephemeral else ""}.modal.run/local_llm"
        )
        response = requests.post(
            base_url,
            headers=headers,
            json={"prompt": prompt},
            params={"vllm": self.vllm, "model": "llama3_8b"},
        )

        if response.status_code >= 200 and response.status_code < 300:
            response = response.json()
            self.history.append(
                {
                    "prompt": prompt,
                    "response": {"choices": response["content"]},
                    "kwargs": kwargs,
                }
            )
            return response
        else:
            print("Response Error / code:", response.status_code)
            return

    def __call__(self, prompt, **kwargs):
        response = self.basic_request(prompt, **kwargs)

        completions = [result["text"] for result in response["content"]]

        return completions
