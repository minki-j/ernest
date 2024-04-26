import requests

from dsp import LM


class Llama3_8b_Modal_Client(LM):
    def __init__(self):
        self.provider = "default"
        self.history = []
        self.base_url = "https://jung0072--survey-buddy-fastapi-asgi-dev.modal.run/local_llm"
        self.kwargs ={}
        print("Class Initialized: Llama3_8b_Modal_Client")

    def basic_request(self, prompt: str, **kwargs):
        print("basic_request function called")
        headers = {"content-type": "application/json"}

        response = requests.post(
            self.base_url,
            headers=headers,
            json={"prompt": prompt},
        )
        print("ran until here")
        response = response.json()
        print("response: ", response)

        self.history.append(
            {
                "prompt": prompt,
                "response": response,
                "kwargs": kwargs,
            }
        )
        return response

    def __call__(self, prompt, **kwargs):
        print("__call__ function called")
        response = self.basic_request(prompt, **kwargs)

        completions = [result["text"] for result in response["content"]]

        return completions
