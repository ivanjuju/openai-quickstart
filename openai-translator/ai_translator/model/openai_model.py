import openai
import requests
import simplejson
import time

from tenacity import retry, wait_random_exponential, stop_after_attempt

from utils import LOG
from model import Model


class OpenAIModel(Model):
    def __init__(self, model: str, api_key: str):
        self.model = model
        openai.api_key = api_key

    @retry(wait=wait_random_exponential(multiplier=60, max=60), stop=stop_after_attempt(3))
    def make_request_by_message(self, messages: list):
        if not messages:
            raise Exception("the messages parameter must be specified")
        if not self.model.startswith("gpt-3.5-turbo") and not self.model.startswith("gpt-4"):
            raise Exception("GPT model doesn't support calling this method.")
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,

        )
        return response.choices[0].message['content'].strip(), True

    def make_request(self, prompt):
        attempts = 0
        while attempts < 3:
            try:
                if self.model == "gpt-3.5-turbo":
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    translation = response.choices[0].message['content'].strip()
                else:
                    response = openai.Completion.create(
                        model=self.model,
                        prompt=prompt,
                        max_tokens=150,
                        temperature=0
                    )
                    translation = response.choices[0].text.strip()

                return translation, True
            except openai.error.RateLimitError:
                attempts += 1
                if attempts < 3:
                    LOG.warning("Rate limit reached. Waiting for 60 seconds before retrying.")
                    time.sleep(60)
                else:
                    raise Exception("Rate limit reached. Maximum attempts exceeded.")
            except requests.exceptions.RequestException as e:
                raise Exception(f"请求异常：{e}")
            except requests.exceptions.Timeout as e:
                raise Exception(f"请求超时：{e}")
            except simplejson.errors.JSONDecodeError as e:
                raise Exception("Error: response is not valid JSON format.")
            except Exception as e:
                raise Exception(f"发生了未知错误：{e}")
        return "", False
