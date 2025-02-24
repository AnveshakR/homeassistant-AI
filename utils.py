import wakeonlan
from typing import Literal
import matplotlib as mpl
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv
import os
import logging

load_dotenv()

LAPTOP_MAC = os.getenv("MAC_ADDRESS")
LIGHT_MODES = {"breathing single color": "breathing", 
               "solid single color": "solid", 
               "christmas": "christmas", 
               "rgb spectrum": "spectrum"}
LIGHT_COLORS = tuple(mpl.colors.cnames.keys())

@tool
def wake_laptop(wake: bool = True):
    """Wake the laptop"""
    if wake:
        wakeonlan.send_magic_packet(LAPTOP_MAC)
        logging.info(f"Sent packet to {LAPTOP_MAC}")
    
@tool
def set_mood_light(
    light_type: Literal[*LIGHT_MODES.keys(), None] = None,
    color_name: Literal[*LIGHT_COLORS, None] = None
    ):
    """
    Return a light mode and color for the mood light, or None for either if not specified.
    """
    web_led_url = open('curr_url', 'r').readline()
    post_data = dict()
    if light_type is not None:
        post_data['display_input'] = LIGHT_MODES[light_type]
    if color_name is not None and color_name in mpl.colors.cnames:
        post_data['picker_input'] = mpl.colors.cnames[color_name]
    
    requests.post(f"{web_led_url}/update", data=post_data)
    
    logging.info(f"POSTing to {web_led_url}/update with data: {post_data}")
    
tools = [
    wake_laptop,
    set_mood_light
]
