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

Input `:exit` to exit, and the conversation context will be saved to `conversation_ctx.json`.

You can load an conversation context file throuth `-c`, e.g. `-c conversation_ctx.json`

You can input `:file:` before a content file name as the input message's content. e.g `file:prompts_template_0.txt`

Ensure the save conversation history data, you can input `:save` to save conversation context data.
