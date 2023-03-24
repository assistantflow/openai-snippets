import openai
import decorators
import asyncio
import os
import sys
import click


@click.group()
@click.option('--base_url', required=False, default='https://api.openai.com')
def main(base_url):
    openai.api_base = base_url + "/v1"
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        print('no key env set, exit ...')
        sys.exit(-1)
    openai.api_key = os.getenv("OPENAI_API_KEY")


@main.command()
@click.argument('content', required=True)
@click.option('--stream', required=False, default=True, type=bool)
@decorators.coro
async def chat(content, stream):
    completions = await openai.ChatCompletion.acreate(
        model='gpt-3.5-turbo',
        messages=[{"role": "user", "content": content}],
        stream=stream
    )
    if stream:
        async for c in completions:
            sys.stdout.write(c.choices[0].delta.get('content', ''))
            sys.stdout.flush()
    else:
        print(completions.choices[0].message.content)
    print()


@main.command
@click.argument('prompt', required=True)
@click.option('--max_tokens', required=False, default=1024, show_default=True)
@click.option('--temperature', required=False, default=0.5, show_default=True)
@click.option('--stream', required=False, default=True, type=bool)
@decorators.coro
async def complete(prompt, max_tokens, temperature, stream):
    completions = await openai.Completion.acreate(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=stream
    )
    if stream:
        async for c in completions:
            sys.stdout.write(c.choices[0].text)
            sys.stdout.flush()
    else:
        print(completions.choices[0].text)
    print()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
