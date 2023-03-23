import os
import requests
import json
import sys
import click


@click.group()
@click.option('--base_url', required=False, default='https://api.openai.com')
@click.pass_context
def openai(ctx, base_url):
    ctx.ensure_object(dict)
    ctx.obj['URL'] = base_url
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        print('no key env set, exit ...')
        sys.exit(-1)
    ctx.obj['KEY'] = key


@openai.command()
@click.argument('content', required=True)
@click.option('--stream', required=False, default=True, type=bool)
@click.pass_context
def chat(ctx, content, stream):
    with requests.Session().post(
            ctx.obj['URL']+'/v1/chat/completions',
            headers={'Authorization': 'Bearer {}'.format(ctx.obj['KEY'])},
            stream=stream,
            json={
                "model": "gpt-3.5-turbo",
                "stream": stream,
                "messages": [{"role": "user", "content": content}],
            }) as resp:
        for line in resp.iter_lines():
            v = line[len('data: '):]
            if v and v != b"[DONE]":
                s = json.loads(v)
                if 'choices' in s:
                    c = s['choices'][0]['delta'].get('content', '')
                    sys.stdout.write(c)
                    sys.stdout.flush()


if __name__ == '__main__':
    openai()
