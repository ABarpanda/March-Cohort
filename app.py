from smolagents import CodeAgent, DuckDuckGoSearchTool, load_tool, tool, Tool
import datetime
import requests
from dotenv import load_dotenv
import os
import pytz
import yaml
from tools.final_answer import FinalAnswerTool
from together import Together
import tools.mytools as mytools
from Gradio_UI import GradioUI

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

            '''
            client = Together()
            response = client.completions.create(
                model="mistralai/Mixtral-8x7B-v0.1",
                prompt="[]",
                max_tokens=None,
                temperature=0.7,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stop=[],
                stream=True
            )
            for token in response:
                if hasattr(token, 'choices'):
                    print(token.choices[0].delta.content, end='', flush=True)
            '''

            # Properly formatted messages list
            '''
            messages=
                [
                    {"role":"user","content":"Hi\n"},
                    {"role":"assistant","content":"It's nice to meet you. Is there something I can help you with or would you like to chat?"},
                    {"role":"user","content":""}
                ]
            '''
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

            # Log the raw response for debugging
            # print("Raw Response:", response)

            # Extract the content safely
            if response.choices:
                return response.choices[0].message#.content

            return "Error: No valid choices in the response."

        except Exception as e:
            print(f"Error generating output: {e}")
            return "Error: Model generation failed."

# Below is an example of a tool that does nothing. Amaze us with your creativity!
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

# Final Answer Tool
final_answer = FinalAnswerTool()

# Initialize Together AI Model
model = TogetherApiModel(
    model_id='meta-llama/Llama-3.3-70B-Instruct-Turbo',#'mistralai/Mixtral-8x7B-Instruct-v0.1',  # Use a supported Together AI model
    temperature=0.5,
    max_tokens=2096
)


# Import tool from Hugging Face Hub
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

# Load prompt templates
with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

# Collect all tools from mytools
tool_list = [final_answer, DuckDuckGoSearchTool(), get_current_time_in_timezone]  # Basic tools

# Dynamically add all callable tools from mytools
# tool_list.extend([obj for obj in vars(mytools).values() if callable(obj)])
# tool_list.sort()
# Remove initial non-tool callables if needed
# for _ in range(4):
#     tool_list.pop(0)
for obj in vars(mytools).values():
    if isinstance(obj, Tool):
        tool_list.append(obj)
        # print(obj.name)
tool_list.remove(mytools.trainBetweenStations)
tool_list.remove(mytools.checkSeatAvailability)

# Output the valid tools
# for i in tool_list:
#     print(i.name)

# Initialize Code Agent
agent = CodeAgent(
    model=model,
    tools=tool_list,
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name="Om Tours Travel Agent",
    description="A travel agent to prepare custom itenaries",
    prompt_templates=prompt_templates
)


GradioUI(agent).launch()