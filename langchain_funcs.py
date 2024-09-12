from langchain_core.documents.base import Blob
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser
from langchain_openai import ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field
from langchain.chains.openai_functions import create_structured_output_chain
from langchain.prompts import PromptTemplate
from typing import Optional
import requests

from dotenv import load_dotenv
import os
import asyncio

import matplotlib as mpl
import argparse

load_dotenv()

openai_api_key = os.getenv("OPENAI_SECRET")


async def function_call_from_user_prompt(user_prompt):
    template = """
    You will be given an instruction from a user.
    You have to infer a structured output from keywords in the instruction. 
    You have to infer a color name from the keywords which has to be one of these colors: {colors}

    % USER INPUT:
    {user_input}

    YOUR RESPONSE:
    """

    prompt = PromptTemplate(
        input_variables=["user_input"],
        partial_variables={"colors":", ".join(mpl.colors.cnames.keys())},
        template=template
    )

    llm = ChatOpenAI(model='gpt-3.5-turbo', openai_api_key=openai_api_key)

    # stores lighting type and color
    class LightClass(BaseModel):
        light_type: Optional[str] = Field(None, description="Lighting type (breathing, solid")
        color_name: Optional[str] = Field(None, description="color name")
        
    chain = create_structured_output_chain(LightClass, llm, prompt)

    web_led_url = open('curr_url', 'r').readline()

    post_data = dict()
    
    output = chain.invoke(user_prompt)['function']
    print(output)
    
    if output.light_type is not None:
        post_data['display_input'] = output.light_type
    
    if output.color_name is not None and output.color_name in mpl.colors.cnames:
        post_data['picker_input'] = mpl.colors.cnames[output.color_name]
        
    print(post_data)
    
    requests.post(f"{web_led_url}/update", data=post_data)
            
            
async def user_prompt_from_audio(user_audio_path, perform_function_call=True, delete_after=False):  
    blob = Blob.from_path(user_audio_path)

    parser = OpenAIWhisperParser(api_key=openai_api_key, chunk_duration_threshold=1)

    documents = parser.lazy_parse(blob)

    user_prompt = " ".join(doc.page_content for doc in documents)

    print(user_prompt)
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
        asyncio.run(function_call_from_user_prompt("Make them dark red"))