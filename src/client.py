import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class GroqClient:
    def __init__(self, base_url=None):
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY is not set. Copy .env.example to .env and add the key.")
        if base_url and "api.groq.com" not in base_url:
            self.client = Groq(api_key=key, base_url=base_url)
        else:
            self.client = Groq(api_key=key)

    def chat(self, model, prompt, temperature=0.2, max_completion_tokens=512, reasoning_effort=None, reasoning_format=None):
        kwargs = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_completion_tokens": max_completion_tokens,
        }
        if reasoning_effort:
            kwargs["reasoning_effort"] = reasoning_effort
        if reasoning_format:
            kwargs["reasoning_format"] = reasoning_format

        r = self.client.chat.completions.create(**kwargs)
        u = getattr(r, "usage", None)
        return {
            "text": r.choices[0].message.content or "",
            "usage": {
                "prompt_tokens": getattr(u, "prompt_tokens", None) if u else None,
                "completion_tokens": getattr(u, "completion_tokens", None) if u else None,
                "total_tokens": getattr(u, "total_tokens", None) if u else None,
            },
        }
