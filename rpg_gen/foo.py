from pydantic import BaseModel
from openai import OpenAI
client = OpenAI()

class Step(BaseModel):
    explanation: str
    output: str

class MathReasoning(BaseModel):
    steps: list[Step]
    final_answer: str



class DmTurn(BaseModel):
	new_plot_log_entries: list[PlotLogEntry]
	scene_transition: str
	output_for_user: str

class UserInput(BaseModel):
	input: str

class Context(BaseModel):
	character_sheet: str
	setting_base: list[str]
	plot_log: list[PlotLogEntry]
	def get_messages:
		return []


# context = Context... how do you make objects in python lol

completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=context.get_messages,
    response_format=DmTurn,
)

math_reasoning = completion.choices[0].message

# If the model refuses to respond, you will get a refusal message
if (math_reasoning.refusal):
    print(math_reasoning.refusal)
else:
    print(math_reasoning.parsed)