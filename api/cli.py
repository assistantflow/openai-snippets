from utils import num_tokens_from_string, num_tokens_from_messages
from decorators import coro
import openai
import asyncio
import os
import sys
import click


@click.group()
@click.option('--base_url', required=False, default='https://api.openai.com')
def main(base_url: str):
    openai.api_base = base_url + "/v1"
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        print('no key env set, exit ...')
        sys.exit(-1)
    openai.api_key = os.getenv("OPENAI_API_KEY")


@main.command()
@click.argument('content', required=True)
@click.option('--model', required=False, default='gpt-3.5-turbo', show_default=True, type=click.Choice(['gpt-3.5-turbo', 'gpt-4']), show_choices=True)
@click.option('--stream', required=False, default=True, show_default=True, type=bool)
@coro
async def chat(content: str, model: str, stream: bool):
    completions_to_token = ''
    messages = [{"role": "user", "content": content}]
    completions = await openai.ChatCompletion.acreate(
        model=model,
        messages=messages,
        stream=stream
    )
    if stream:
        async for c in completions:
            ct = c.choices[0].delta.get('content', '')
            sys.stdout.write(ct)
            sys.stdout.flush()
            completions_to_token = f'{completions_to_token}{ct}'
    else:
        ct = completions.choices[0].message.content
        print(ct)
        completions_to_token = f'{completions_to_token}{ct}'

    prompt_tokens = num_tokens_from_messages(messages, model)
    completion_tokens = num_tokens_from_string(completions_to_token, model)
    total_tokens = prompt_tokens + completion_tokens
    sp = '=' * 10
    print('\n\n{} prompt_tokens: {}, completion_tokens: {}, total_tokens: {} {}'.format(
        sp, prompt_tokens, completion_tokens, total_tokens, sp))


@main.command
@click.argument('prompt', required=True)
@click.option('--model', required=False, default='text-davinci-003', show_default=True, type=click.Choice(['text-davinci-003']), show_choices=True)
@click.option('--max_tokens', required=False, default=1024, show_default=True)
@click.option('--temperature', required=False, default=0.5, show_default=True)
@click.option('--stream', required=False, default=True, show_default=True, type=bool)
@coro
async def complete(prompt: str, model: str, max_tokens: int, temperature: float, stream: bool):
    prompt_to_token = prompt
    completions_to_token = ''
    contents_to_token = prompt_to_token
    completions = await openai.Completion.acreate(
        engine=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=stream
    )
    if stream:
        async for c in completions:
            ct = c.choices[0].text
            sys.stdout.write(ct)
            sys.stdout.flush()
            completions_to_token = f'{completions_to_token}{ct}'
            contents_to_token = f'{contents_to_token}{ct}'
    else:
        ct = completions.choices[0].text
        print(ct)
        completions_to_token = f'{completions_to_token}{ct}'
        contents_to_token = f'{contents_to_token}{ct}'

    prompt_tokens = num_tokens_from_string(prompt_to_token, model)
    completion_tokens = num_tokens_from_string(completions_to_token, model)
    total_tokens = prompt_tokens + completion_tokens
    sp = '=' * 10
    print('\n\n{} prompt_tokens: {}, completion_tokens: {}, total_tokens: {} {}'.format(
        sp, prompt_tokens, completion_tokens, total_tokens, sp))


def loop():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


if __name__ == '__main__':
    loop()
