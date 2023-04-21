# gpt-4-pybot

## Install

```
pip install -r requirements.txt
```

## Get start

Fill your API key to `.env`, see sample file `.evn.sample`. And make sure your API key can call GPT-4.

```
python3 run_gpt4_chatbot.py
```

You can load an conversation context file through `-c`, e.g. `-c conversation_ctx.json`

You can choice use OpenAI Python sdk or use the OpenAI API by `request` through `-t`, default `api` e.g. `-t sdk`

You can change model through `-m`, e.g. `-c text-davince-003`, default `gpt-4`. Make sure the model supported chatbot mode.

Input `:exit` to exit, and the conversation context will be saved to `conversation_ctx.json`.

You can input `:file:` before a content file name as the input message's content. e.g `file:prompts_template_0.txt`

Ensure the save conversation history data, you can input `:save` to save conversation context data.

Input `:regen` to regenerate the last response.

Input `:history` to show all conversation history.