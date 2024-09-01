from langchain_core.documents.base import Blob
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser
from langchain_openai import ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field
from langchain.chains.openai_functions import create_structured_output_chain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
from typing import Optional
import requests

from dotenv import load_dotenv
import os
import asyncio

import matplotlib as mpl

load_dotenv()

openai_api_key = os.getenv("OPENAI_SECRET")


async def function_call_from_user_prompt(user_prompt):
    response_schemas = [
        ResponseSchema(name="bad_string", description="This a poorly formatted user input string"),
        ResponseSchema(name="good_string", description="This is your response, a reformatted response")
    ]

    # How you would like to parse your output
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

    # See the prompt template you created for formatting
    format_instructions = output_parser.get_format_instructions()

    template = """
    You will be given a poorly formatted string from a user.
    Reformat it and make sure all the words are spelled correctly

    {format_instructions}

    % USER INPUT:
    {user_input}

    YOUR RESPONSE:
    """

    prompt = PromptTemplate(
        input_variables=["user_input"],
        partial_variables={"format_instructions": format_instructions},
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
    
    if output.color_name is not None and output.color_name in user_prompt and output.color_name in mpl.colors.cnames:
        post_data['picker_input'] = mpl.colors.cnames[output.color_name]
        
    print(post_data)
    
    requests.post(f"http://{web_led_url}/update", data=post_data)
            
            
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
    asyncio.run(function_call_from_user_prompt("Make them breathing red"))