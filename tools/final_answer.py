from typing import Any, Optional
from smolagents.tools import Tool

class FinalAnswerTool(Tool):
    name = "final_answer"
    description = "Provides a final answer to the given problem."
    inputs = {'answer': {'type': 'any', 'description': 'The final answer to the problem'}}
    output_type = "any"

    def forward(self, answer: Any) -> Any:
        print("✅ Final Output:", answer)
        return answer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("Final Answer Tool initialised successfully ✅")
        self.is_initialized = True

    def __call__(self, answer):
        # Capture and log the full output
        with open("final_output.json", "w") as file:
            file.write(str(answer))
        print("Final Answer:", answer)
        return answer