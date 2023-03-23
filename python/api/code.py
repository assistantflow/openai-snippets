import os
import requests
import json
import sys
from typing import Iterator

key = os.getenv("OPENAI_API_KEY")


def get_stream(url) -> Iterator[str]:
    s = requests.Session()

    with s.post(
        url,
        headers={"Authorization": "Bearer {}".format(key)},
        stream=True,
        json={
            "model": "gpt-3.5-turbo",
            "stream": True,
            "messages": [{"role": "user", "content": "你好"}],
        },
    ) as resp:
        for line in resp.iter_lines():
            v = line[len('data: '):]
            if v and v != b"[DONE]":
                s = json.loads(v)
                if 'choices' in s:
                    yield s['choices'][0]['delta'].get('content', '')


if __name__ == "__main__":
    url = "https://api.openai.com/v1/chat/completions"
    for v in get_stream(url):
        sys.stdout.write(v)
        sys.stdout.flush()
