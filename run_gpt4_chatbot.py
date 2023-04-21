import datetime
import itertools
import os
import openai
from dotenv import load_dotenv
import asyncio
import json
import sys
import argparse
import requests
import threading
from concurrent.futures import ThreadPoolExecutor

load_dotenv()
parser = argparse.ArgumentParser(description='Chat to GPT4')
parser.add_argument('-m', '--model',
                    help='Model Id, default gpt-4')
parser.add_argument('-t', '--tool',
                    help='Use sdk or http api (sdk or api), default api')
args = parser.parse_args()
if args.model == None:
    model = 'gpt-4'
else:
    model = args.model
if args.tool == None:
    tool = 'api'
else:
    tool = args.tool


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


def spinning_slash(stop_event):
    spinning_chars = itertools.cycle(['/', '-', '\\', '|'])
    while not stop_event.is_set():
        sys.stdout.write(next(spinning_chars))
        sys.stdout.flush()
        stop_event.wait(0.1)
        sys.stdout.write('\b')


async def spinning_loading():
    print_colored_text("Loading...\n", "yellow")

openai.api_key = os.getenv("OPENAI_API_KEY")


async def chatToModel(_ctx, model):
    try:
        response = openai.ChatCompletion.create(
            # model="davinci:ft-personal:metapath-2023-03-28-02-42-17",
            model=model,
            messages=_ctx,
            temperature=1
        )
    except all as e:
        print_colored_text(
            f"Catch Exception {type(e).__name__}, Info: {e}", "red")
        return None
    finally:
        return response


async def chatToModelHttp(_ctx, model):
    url = 'https://api.openai.com/v1/chat/completions'

    data = {
        'model': model,
        'messages': _ctx
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+os.getenv("OPENAI_API_KEY")
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
    except all as e:
        print_colored_text(
            f"Catch Exception {type(e).__name__}, Info: {e}", "red")
        return None
    finally:
        return response.json()


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


async def main(model, tool):
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
        print_colored_text("="*100, "blue")
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
        stop_event = threading.Event()
        with ThreadPoolExecutor(max_workers=1) as executor:
            spinner_thread = executor.submit(spinning_slash, stop_event)
            try:
                if tool == 'api':
                    task = chatToModelHttp(_ctx=context, model=model)
                if tool == 'sdk':
                    task = chatToModel(_ctx=context, model=model)
                gpt4_task = asyncio.create_task(task)
                response = await gpt4_task
                stop_event.set()
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
                stop_event.set()
            finally:
                spinner_thread.cancel()
                stop_event.set()
asyncio.run(main(model=model, tool=tool))
