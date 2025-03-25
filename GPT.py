import openai
import os
import dotenv
import logging

dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('\x1b[36m{asctime} {levelname:<8} {name}: \x1b[37m{message}\x1b[0m', dt_fmt, style='{')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

dotenv.load_dotenv()

class GPT:
    def __init__(self) -> None:
        self._gpt = openai.OpenAI(api_key=os.getenv("GPTTOKEN"))
        self.base_prompt_path = "base_prompt.txt"
        with open(self.base_prompt_path, "r") as f:
            self.base_prompt = f.read()
        self.chat_history = []
        self.model = os.getenv("GPTMODEL")
        self.history_limit = int(os.getenv("LIMIT"))
    
    def load_prompt(self) -> None:
        with open(self.base_prompt_path, "r") as f:
            self.base_prompt = f.read()
        log.info("Prompt loaded")
    
    def message_request(self, message:str, user:str) -> str:
        if len(self.chat_history) > self.history_limit:
            self.chat_history = []
            log.info("History cleared")
        if len(self.chat_history) == 0:
            self.chat_history.append({"role": "user", "content": "{} {} : {}".format(self.base_prompt, user, message)})
        else:
            self.chat_history.append({"role": "user", "content": str(user+" : "+message)})
        response = self._send_message(self.chat_history)
        content = response.choices[0].message.content
        self.chat_history.append({"role": "assistant", "content": content})
        log.info(response.usage)
        return content
    
    def _send_message(self, message:str):
        completion = self._gpt.chat.completions.create(
        messages=message,
        model=self.model,
        max_tokens=1024,
        temperature=0.7,
        )
        return completion
    
    def clear_history(self):
        self.chat_history = []

    def change_base_prompt(self, path):
        self.base_prompt_path = path