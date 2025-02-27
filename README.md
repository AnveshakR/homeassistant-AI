# Home Assistant AI

Didn't want to rely on a third party service like Google Home or Alexa so I made my own modular framework.

- Speech-to-text with [OpenAI Whisper](https://platform.openai.com/docs/models#whisper)
- Text-to-text with [OpenAI GPT-4o mini](https://platform.openai.com/docs/models#gpt-4o-mini)
- [LangChain](https://www.langchain.com/langchain) for modular tool calling
- [Tailscale](https://tailscale.com/) for remote access via Apple Shortcuts
- Optional Discord bot with voice clipping (have to call via command, keyword recognition not anytime soon)

Minimum Python version - 3.11.x

/utils.py is used to setup custom functions and tools for those chains. /langchain_funcs.py doesn't really need to be changed as all the "important" variables are deferred to the .env file, unless you want to switch to a different LLM provider/custom LLM.

> Note: Setting this up in your own environment means that you take the responsibility of implementing the necessary security and privacy protocols. I have my own setup figured out, feel free to ask me for help but I am not to blame for foolishness or any problems it might cause :) 