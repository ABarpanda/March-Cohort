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
from smolagents.models import ChatMessage

import os
from dotenv import load_dotenv
from together import Together
from smolagents.models import ChatMessage


class TogetherApiModel:
    def __init__(self, model_id: str, temperature: float = 0.7, max_tokens: int = 2048):
        """
        Together AI model wrapper for text generation, compatible with smolagents' CodeAgent.

        Args:
            model_id (str): Together AI model ID (e.g., 'meta-llama/Llama-3.3-70B-Instruct-Turbo').
            temperature (float): Sampling temperature (higher = more creative).
            max_tokens (int): Maximum length of the generated output.
        """
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens

        load_dotenv()
        api_key = os.getenv("TOGETHER_API_KEY") or os.getenv("together_api_key")
        if not api_key:
            raise ValueError(
                "TOGETHER_API_KEY not found in environment. Check your .env file's key name matches exactly."
            )
        self.client = Together(api_key=api_key)
        print("TogetherApiModel initialised successfully ✅")

    def _flatten_content(self, content):
        """
        Flattens a single message's content into a plain string.
        smolagents sends content as either a plain string or a list of
        content blocks like [{"type": "text", "text": "..."}].
        """
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and "text" in block:
                    parts.append(block["text"])
                elif isinstance(block, str):
                    parts.append(block)
            return "\n".join(parts)
        return str(content)

    def _build_messages(self, messages):
        """
        Converts smolagents' message list into Together/OpenAI-style messages,
        preserving each message's role (system/user/assistant) instead of
        collapsing the whole conversation into a single user turn.
        """
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]

        if not isinstance(messages, list):
            raise ValueError(f"Invalid messages format: {type(messages)}")

        built = []
        for msg in messages:
            # smolagents feeds back a mix of plain dicts (fresh messages) and
            # ChatMessage objects (its own memory of prior assistant turns) —
            # dicts support .get(), ChatMessage only supports attribute access.
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
            else:
                role = getattr(msg, "role", "user")
                content = getattr(msg, "content", "")

            # role may itself be a MessageRole enum in some smolagents versions
            role = getattr(role, "value", role)
            if role not in ("system", "user", "assistant", "tool"):
                role = "user"

            text = self._flatten_content(content)
            if text.strip():
                built.append({"role": role, "content": text})

        if not built:
            raise ValueError("No valid messages to send after flattening.")
        return built

    def __call__(self, messages, stop_sequences=None, grammar=None, tools_to_call_from=None, **kwargs) -> ChatMessage:
        """
        smolagents calls the model as a callable: model(messages, stop_sequences=..., ...).
        This is the required entry point — a `generate`-only class will raise
        'object is not callable' the first time CodeAgent tries to run a step.
        """
        try:
            chat_messages = self._build_messages(messages)

            # Together's API expects `stop`, not `stop_sequences`; it doesn't
            # support `grammar` or `tools_to_call_from` at all, so those are
            # deliberately not forwarded.
            create_kwargs = dict(
                model=self.model_id,
                messages=chat_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            if stop_sequences:
                create_kwargs["stop"] = stop_sequences

            response = self.client.chat.completions.create(**create_kwargs)

            if not response.choices:
                raise RuntimeError("Together API returned no choices.")

            content = response.choices[0].message.content
            return ChatMessage(role="assistant", content=content)

        except Exception as e:
            # Re-raise rather than returning a fake "Error: ..." string as if
            # it were valid model output — swallowing this here would make
            # CodeAgent try to parse the error text as Python code and fail
            # with a confusing, unrelated error instead of this real one.
            print(f"Error generating output from Together API: {e}")
            raise

    def generate(self, prompt, **kwargs) -> ChatMessage:
        return self.__call__(prompt, **kwargs)

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
    print("Tool list initialised successfully ✅")

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
        planning_interval=None,
        name="Om_Tours_Travel_Agent",
        description="A travel agent to prepare custom itenaries",
        prompt_templates=prompt_templates
    )
    with open("final_output.json","r") as file:
        print("Final Output .json opened successfully ✅")
        itenary_json = file.read()
    
    print("Itenary json:", itenary_json)
    print("Type of itenary json:", type(itenary_json)) #str

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