import requests

from dsp import LM


class Llama3_8b_Modal_Client(LM):
    def __init__(self):
        self.provider = "default"
        self.history = []
        self.base_url = (
            "https://jung0072--survey-buddy-fastapi-asgi.modal.run/local_llm"
        )
        self.kwargs = {}

    def basic_request(self, prompt: str, **kwargs):
        headers = {"content-type": "application/json"}

        response = requests.post(
            self.base_url,
            headers=headers,
            json={"prompt": prompt},
        )

        if response.status_code >= 200 and response.status_code < 300:
            response = response.json()
            self.history.append(
                {
                    "prompt": prompt,
                    "response": response["content"][0]["text"],
                    "kwargs": kwargs,
                }
            )
            return response
        else:
            print("response status code:", response.status_code)
            return 

    def __call__(self, prompt, **kwargs):
        print("__call__ function called")
        response = self.basic_request(prompt, **kwargs)

        completions = [result["text"] for result in response["content"]]

        return completions
