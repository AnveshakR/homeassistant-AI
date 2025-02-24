from langchain_core.documents.base import Blob
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
import os
import asyncio
import argparse
import logging
logging.basicConfig(level=logging.INFO)

from utils import *

load_dotenv()

openai_api_key = os.getenv("LLM_SECRET")
model_name = os.getenv("MODEL_NAME")


async def function_call_from_user_prompt(user_prompt):
    llm = ChatOpenAI(api_key=openai_api_key,
                     model=model_name,
                     temperature=0)
    
    # force the agent to use at least one tool
    agent = llm.bind_tools(tools, tool_choice="any")
    
    llm_response = agent.invoke(user_prompt)
    logging.info(llm_response)
    
    # generate tool name vs tool object mapping
    tool_name_to_obj = {tool.name: tool for tool in tools}

    for tool_call in llm_response.tool_calls:

        if tool_call['name'] in tool_name_to_obj:
            tool_response = tool_name_to_obj[tool_call['name']].invoke(tool_call)
            logging.info(tool_response)
        else:
            logging.error(f"Tool {tool_call['name']} not found in tools list.")
           
    return
            
            
async def user_prompt_from_audio(user_audio_path, perform_function_call=True, delete_after=False):  
    blob = Blob.from_path(user_audio_path)

    parser = OpenAIWhisperParser(api_key=openai_api_key, chunk_duration_threshold=1)

    documents = parser.lazy_parse(blob)

    user_prompt = " ".join(doc.page_content for doc in documents)
    logging.info("User prompt from Whisper: " + user_prompt)

    if delete_after:
        os.remove(user_audio_path)    
    if perform_function_call:
        await function_call_from_user_prompt(user_prompt=user_prompt)
    else:
        return user_prompt  
    
       
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="prompt from Apple shortcuts")
    args = parser.parse_args()
    if args.prompt is not None:
        asyncio.run(function_call_from_user_prompt(args.prompt))
    else:
        asyncio.run(function_call_from_user_prompt("start laptop"))