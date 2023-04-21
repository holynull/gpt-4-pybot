import datetime
import itertools
import os
import openai
from dotenv import load_dotenv
import asyncio
import json
import sys
import argparse
import os
import httpx
import json
from typing import List

load_dotenv()
parser = argparse.ArgumentParser(description='Chat to GPT4')
parser.add_argument('-m', '--model',
                    help='Model Id, default gpt-4')
args = parser.parse_args()
if args.model == None:
    model = 'gpt-4'
else:
    model = args.model


def print_colored_text(text, color):
    color_code = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m",
    }
    print(f"{color_code[color]}{text}{color_code['reset']}")


async def spinning_slash():
    spinning_chars = itertools.cycle(['/', '-', '\\', '|'])
    while True:
        sys.stdout.write(next(spinning_chars))
        sys.stdout.flush()
        # stop_event.wait(0.1)
        await asyncio.sleep(0.1)
        sys.stdout.write('\b')


async def spinning_loading():
    print_colored_text("Loading...\n", "yellow")

openai.api_key = os.getenv("OPENAI_API_KEY")


async def chatToModelHttp(_ctx: List[dict], model: str):
    url = 'https://api.openai.com/v1/chat/completions'

    data = {
        'model': model,
        'messages': _ctx,
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}'
    }
    # timeout = httpx.TimeOut(connect_timeout=5, read_timeout=5 * 60, write_timeout=5)
    timeout = httpx.Timeout(connect=None, read=None, write=None, pool=None)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=timeout)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Catch exception {type(e).__name__}, Info: {e}")
        return None


def saveConversation(ctxFileName, context) -> str:
    if ctxFileName == None or ctxFileName == "":
        _ctxFileName = input(
            "Input your conversation name, or press entern: ")
        if _ctxFileName != None and _ctxFileName != '':
            ctxFileName = _ctxFileName
        else:
            now = datetime.datetime.now()
            ctxFileName = now.strftime("%Y%m%d%H%M%S")
    with open(f"{ctxFileName}.ctx.json", "w") as json_file:
        json.dump(context, json_file)
        print_colored_text(
            f"Save conversation to {ctxFileName}.ctx.json", "blue")
    return ctxFileName


async def main(model):
    context = [
        {"role": "system", "content": "You are a helpful assistant."}]
    ctxFileName = input(
        "Fill your conversation name, or press entern: ")
    if ctxFileName != None and ctxFileName != "":
        try:
            with open(f"{ctxFileName}.ctx.json", "r") as file:
                context = json.load(file)
                print_colored_text(
                    f"Load conversation file {ctxFileName}.ctx.json", "blue")
        except FileNotFoundError as e:
            print_colored_text(
                f"Catch Exception {type(e).__name__}, Info: {e}", "red")
            return
    while True:
        print_colored_text("Send a message: ", "green")
        user_input = input("")
        if user_input == ":exit":
            saveConversation(ctxFileName=ctxFileName, context=context)
            break
        if user_input == ":save":
            try:
                ctxFileName = saveConversation(
                    ctxFileName=ctxFileName, context=context)
            except all as e:
                print_colored_text(
                    f"Catch Exception {type(e).__name__}, Info: {e}", "red")
            continue
        if user_input.startswith(":file:"):
            filename = user_input[len(":file:"):]
            try:
                with open(filename, "r") as prompt_file:
                    user_input = prompt_file.read()
                    print_colored_text("\nFile content:", "cyan")
                    print(user_input)
                    print_colored_text("="*100, "blue")
            except all as e:
                print_colored_text(
                    f"Catch Exception {type(e).__name__}, Info: {e}", "red")
                continue
        if user_input == ":history":
            print_colored_text("\nConversation History:", "blue")
            for c in context:
                print_colored_text(c['role']+":", "green")
                print(c['content'])
            print_colored_text("="*100, "blue")
            continue
        prompt = {"role": "user", "content": user_input}
        if user_input == ":regen":
            prompt = context[len(context)-2]
            context = context[:-1]
            print(prompt["content"])
        else:
            context.append(prompt)
        spinner_task = asyncio.create_task(spinning_slash())
        try:
            task = chatToModelHttp(_ctx=context, model=model)
            task = asyncio.create_task(task)
            response = await task
            if response != None:
                # finish_reason = response['choices'][0]['finish_reason']
                response_txt = response['choices'][0]['message']["content"]
                response_role = response['choices'][0]['message']["role"]
                print_colored_text(f"\nModel-{model}:", "green")
                print(response_txt)
                print_colored_text("="*100, "blue")
                context.append(
                    {"role": response_role, "content": response_txt})
                try:
                    ctxFileName = saveConversation(
                        ctxFileName=ctxFileName, context=context)
                except all as e:
                    print_colored_text(
                        f"Catch Exception {type(e).__name__}, Info: {e}", "red")
                continue
        except all as e:
            print_colored_text(
                f"Catch Exception {type(e).__name__}, Info: {e}", "red")
            spinner_task.cancel()
        finally:
            spinner_task.cancel()
if __name__ == "__main__":
    asyncio.run(main(model=model))
