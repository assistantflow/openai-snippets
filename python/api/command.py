import decorators
import aiohttp
import asyncio
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
@decorators.coro
async def chat(ctx, content, stream):
    async with aiohttp.ClientSession() as session:
        async with session.post(ctx.obj['URL'] + '/v1/chat/completions',
                                headers={'Authorization': 'Bearer {}'.format(ctx.obj['KEY'])},
                                json={
                                    'stream': stream,
                                    "model": "gpt-3.5-turbo",
                                    "messages": [{"role": "user", "content": content}]
        }) as resp:
            if resp.status != 200:
                s = await resp.text()
                print(s)
                return

            async for line in resp.content:
                v = line[len('data: '):]
                if v and not v.startswith(b"[DONE]"):
                    s = json.loads(v)
                    if 'choices' in s:
                        c = s['choices'][0]['delta'].get('content', '')
                        sys.stdout.write(c)
                        sys.stdout.flush()
            print()


@openai.command
@click.argument('prompt', required=True)
@click.option('--max_tokens', required=False, default=1024, show_default=True)
@click.option('--temperature', required=False, default=0.5, show_default=True)
@click.option('--stream', required=False, default=True, type=bool)
@click.pass_context
@decorators.coro
async def complete(ctx, prompt, max_tokens, temperature, stream):
    async with aiohttp.ClientSession() as session:
        async with session.post(ctx.obj['URL'] + '/v1/completions',
                                headers={'Authorization': 'Bearer {}'.format(ctx.obj['KEY'])},
                                json={
                                    'stream': stream,
                                    'model': 'text-davinci-003',
                                    'prompt': prompt,
                                    'max_tokens': max_tokens,
                                    'temperature': temperature}
                                ) as resp:
            if resp.status != 200:
                s = await resp.text()
                print(s)
                return

            async for line in resp.content:
                v = line[len('data: '):]
                if v and not v.startswith(b"[DONE]"):
                    s = json.loads(v)
                    if 'choices' in s:
                        c = s['choices'][0].get('text', '')
                        sys.stdout.write(c)
                        sys.stdout.flush()
            print()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(openai())
