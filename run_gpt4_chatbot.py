import itertools
import os
import openai
from dotenv import load_dotenv
import asyncio
import json
import sys
import argparse

load_dotenv()
parser = argparse.ArgumentParser(description='Chat to GPT4')
parser.add_argument('-c', '--conversation_ctx',
                    help='Conversation context file')
args = parser.parse_args()
conversation_ctx = args.conversation_ctx


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
    # 定义一个斜杠列表
    spinning_chars = itertools.cycle(['/', '-', '\\', '|'])
    # spinning_chars = itertools.cycle('....')
    # 不停地输出旋转斜杠
    while True:
        # print_colored_text(next(spinning_chars), "yellow")
        sys.stdout.write(next(spinning_chars))
        # print_colored_text("Loading....","yellow")
        sys.stdout.flush()
        await asyncio.sleep(0.5)
        sys.stdout.write('\b')


async def spinning_loading():
    print_colored_text("Loading...\n", "yellow")

openai.api_key = os.getenv("OPENAI_API_KEY")
context = [{"role": "system", "content": "You are a helpful assistant."}]
if conversation_ctx != None:
    with open(conversation_ctx, "r") as file:
        context = json.load(file)


async def chatToGPT4(_ctx):
    response = openai.ChatCompletion.create(
        # model="davinci:ft-personal:metapath-2023-03-28-02-42-17",
        model="gpt-4",
        messages=_ctx,
        temperature=1
    )
    return response


async def main():
    while True:
        print_colored_text("\nInput:", "green")
        user_input = input("")
        if user_input == ":exit":
            with open("conversation_ctx.json", "w") as json_file:
                json.dump(context, json_file)
            break
        if user_input == ":save":
            try:
                with open("conversation_ctx.json", "w") as json_file:
                    json.dump(context, json_file)
                continue
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
            except all as e:
                print_colored_text(
                    f"Catch Exception {type(e).__name__}, Info: {e}", "red")
                continue
        sys.stdout.write('\n')
        context.append({"role": "user", "content": user_input})
        spinner_task = asyncio.create_task(spinning_loading())
        try:
            gpt4_task = asyncio.create_task(chatToGPT4(context))
            response = await gpt4_task
            # finish_reason = response['choices'][0]['finish_reason']
            response_txt = response['choices'][0]['message']["content"]
            response_role = response['choices'][0]['message']["role"]
            print_colored_text("\nGPT-4:", "green")
            print(response_txt)
            context.append({"role": response_role, "content": response_txt})
        except all as e:
            print_colored_text(
                f"Catch Exception {type(e).__name__}, Info: {e}", "red")
        finally:
            spinner_task.cancel()
asyncio.run(main())
