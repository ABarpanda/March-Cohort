from smolagents import CodeAgent, DuckDuckGoSearchTool, tool, Tool
import datetime
import requests
from dotenv import load_dotenv
import os
import sys
import pytz
import yaml
from tools.final_answer import FinalAnswerTool
from together import Together
import tools.mytools as mytools
import json

class TogetherApiModel:
    def __init__(self, model_id: str, temperature: float = 0.7, max_tokens: int = 2048):
        """
        Together AI model wrapper for text generation.

        Args:
            model_id (str): Together AI model ID (e.g., 'meta-llama/Llama-3.3-70B-Instruct-Turbo').
            temperature (float): Sampling temperature (higher = more creative).
            max_tokens (int): Maximum length of the generated output.
        """
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens

        load_dotenv()
        self.client = Together(api_key=os.getenv("together_api_key"))

    def extract_prompt(self, prompt):
        """
        Extracts and flattens the prompt if it's provided as a list of messages.

        Args:
            prompt (str | list): Input prompt or list of conversation messages.

        Returns:
            str: Flattened prompt as a single string.
        """
        if isinstance(prompt, list):
            # Flatten list of messages to a single string
            return "\n".join(
                f"{msg['role'].capitalize()}: {msg['content'][0]['text']}"
                for msg in prompt
                if 'content' in msg and isinstance(msg['content'], list)
            )
        if isinstance(prompt, str):
            return prompt

        raise ValueError("Invalid prompt format. Must be a string or a list of messages.")

    def __call__(self, prompt: str, **kwargs) -> str:
        """
        Generates output using the Together AI model.

        Args:
            prompt (str | list): Input text prompt (or message list for conversations).
            **kwargs: Additional options (e.g., stop_sequences).

        Returns:
            str: Generated output from the model.
        """
        try:
            # Flatten the prompt if it's a list
            prompt_text = self.extract_prompt(prompt)

            # Ensure the prompt is valid
            if not isinstance(prompt_text, str) or not prompt_text.strip():
                raise ValueError(f"Invalid prompt after extraction: {prompt_text} (Type: {type(prompt_text)})")
            
            messages = [{"role": "user", "content": prompt_text}]
            # print(f"Sending prompt to Together AI: {messages}")

            # Call the Together AI API
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )

            if response.choices:
                return response.choices[0].message

            return "Error: No valid choices in the response."

        except Exception as e:
            print(f"Error generating output: {e}")
            return "Error: Model generation failed."

@tool
def my_custom_tool(arg1: int, arg2: int) -> str:
    """A tool that multiplies 2 numbers
    Args:
        arg1: the first argument
        arg2: the second argument
    """
    return arg1 * arg2

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        tz = pytz.timezone(timezone)
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"

def safe_json_parse(json_str):
    try:
        # First try direct parse
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            fixed = json_str.replace("\'", '\"')  # Single to double quotes
            fixed = fixed.replace(",}", "}")    # Remove trailing commas
            return (fixed)
        except json.JSONDecodeError as e:
            print(f"Could not parse JSON. Error: {e}")
            print(f"Problematic JSON: {json_str[:200]}...")
            return None

def Main(destination, start_date, end_date, number_of_people, purpose, budget, location, mode_of_transport):
# def Main():

    final_answer = FinalAnswerTool()

    model = TogetherApiModel(
        model_id='meta-llama/Llama-3.3-70B-Instruct-Turbo',
        temperature=0.5,
        max_tokens=2096
    )

    with open("prompts.yaml", 'r') as stream:
        prompt_templates = yaml.safe_load(stream)

    tool_list = [final_answer, DuckDuckGoSearchTool(), get_current_time_in_timezone] 

    for obj in vars(mytools).values():
        if isinstance(obj, Tool):
            tool_list.append(obj)
            # print(obj.name)
    tool_list.remove(mytools.trainBetweenStations)
    tool_list.remove(mytools.checkSeatAvailability)

    agent = CodeAgent(
        model=model,
        tools=tool_list,
        additional_authorized_imports = ["json"],
        max_steps=10,
        verbosity_level=3,
        grammar=None,
        planning_interval=None,
        name="Om Tours Travel Agent",
        description="A travel agent to prepare custom itenaries",
        prompt_templates=prompt_templates
    )
    with open("final_output.json","r") as file:
        itenary_json = file.read()
    
    print(itenary_json)
    if type(itenary_json)==str:
        print("string",json.loads(itenary_json))
    elif type(itenary_json)==dict:
        print("dict", json.load(itenary_json))
    else:
        print("Itenary json is neither dict nor str")

    response = agent.run(f"Plan a trip to {destination} for {number_of_people} people from {start_date} to {end_date} and prepare a custom itenary in the given format. They are currently in {location} and want to travel by {mode_of_transport} for {purpose}. Divide the budget of {budget} accordingly.")
    # GradioUI(agent).launch()
    print("Response from agent:", response)
    print("Type of response:", type(response))
    print("safe_json_parse response:", safe_json_parse(str(response)))
    print("Type of safe_json_parse response:", type(safe_json_parse(str(response))))
    print("Final response:", json.loads(str(safe_json_parse(str(response)))))
    print("Type of final response:", type(json.loads(str(safe_json_parse(str(response))))))
    return json.loads(str(safe_json_parse(str(response))))


if __name__=="__main__":
    Main(
        destination="Goa",
        start_date="2025-04-01",
        end_date="2025-04-05",
        number_of_people=2,
        purpose="vacation",
        budget="20000",
        location="Mumbai",
        mode_of_transport="flight"
    )