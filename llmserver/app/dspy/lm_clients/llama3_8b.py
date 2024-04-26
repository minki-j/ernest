import requests

from dsp import LM


class Llama3_8b_Modal_Client(LM):
    def __init__(self):
        self.provider = "default"
        self.history = []
        self.base_url = "https://jung0072--survey-buddy-fastapi-asgi-dev.modal.run/local_llm"
        self.kwargs ={}

    def basic_request(self, prompt: str, **kwargs):
        headers = {"content-type": "application/json"}

        response = requests.post(
            self.base_url,
            headers=headers,
            json={"prompt": prompt},
        )

        response = response.json()
        print("Response from API call for local llama3: ", response)

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
