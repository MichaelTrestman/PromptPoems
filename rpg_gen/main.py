import os
import yaml
import random
from prompt_poet import Prompt
from langchain_openai import ChatOpenAI
from jinja2 import Template

# Uncomment if you need to set OPENAI_API_KEY.
# os.environ["OPENAI_API_KEY"] =

# Load settings, plot hooks, and character sheets from YAML files
def load_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading YAML file {file_path}: {e}")
        return {}


# Function to ensure content is properly formatted for YAML
def format_for_yaml(content):
    return yaml.dump(content, default_flow_style=False).strip()

general_instructions = """

Serve as the DM or Game Runner for an RPG set in this world.
In each round of play, as Game Runner, you should sketch a detailed picture of what player 1 is experiencing on the following 'levels of experience' and then ask what the player wants to do.
Narrate everything in 2nd person, directed towards player one. 

- what concrete details of the situation are immediately obvious, the layout of the immediate surroundings, objects large and small, any tools or weapons or natural items, especially other creatures and people
- what does the characters' bodies currently feel like, their state of energy and any discomfort or pain; also, what drives and urges such as hunger
- what feelings, longings, urges, moods and emotions are the characters experiencing
- what are the thoughts and feelings the characters are experiencing? what memories, current decisions, or hypothetical musings are most salient?

Don't list the levels of experience, and don't use them all every time, just use them as a guide to make sure the scene is grounded experientially.
"""

initial_instruction = """
Below are the setting doc for a text RPG, and the character sheets for the main player (player 1).
Begin play by introducing the world of the campaign and giving a backstory spiel for the player, reviewer their abilities. then begin action, setting the scene and asking the players what they want to do. Narrate everything in 2nd person, directed towards player one. 
"""

continue_instruction = """
Continue as Game Runner for the game, generate the next action sequence, describing things on the 'levels of experience'. When events reach a choice point, ask the player for their action, but don't make any suggstions or give too much guidance.
do not make it easy for the player, instead try to give a sense of weight to their decisions by following the scenario to its logical conclusion. if the player makes a poor decision, it is more fun if they have to face the consequences of their actions by having things not go their way.
Do not allow the player to do anything impossible or cast spells that are not in their character sheet. if they attempt to do anything impossible, tell them why it is impossible and allow them to pick a different move instead of moving the action forward.
If they attempt something that seems chancey, come up with a dice roll that seems fair and roll it for them using the values from their character sheet and any applicable situational modifiers. use the result to determine following events.
"""

responses_path = 'responses.yml'

if os.path.exists(responses_path):
    try:
        with open(responses_path, 'r') as file:
            responses = yaml.safe_load(file) or []
    except Exception as e:
        print(f"Error loading responses from {responses_path}: {e}")
        responses = []
else:
    responses = []



setting_doc = load_yaml('prior_setting_doc.yml').get('prior_setting', [])
character_sheet = load_yaml('prior_character_sheets.yml').get('character_sheets', [])[0]

if len(character_sheet) == 0:
	character_sheets_list = load_yaml('character_sheets.yml').get('character_sheets', [])
	character_sheet = random.sample(character_sheets_list, 1)    

def build_context(setting_doc, character_sheet):

    if not setting_doc:
        print("setting doc not detected")
        settings_data = load_yaml('settings.yml').get('settings', [])
        # Check if data is loaded correctly
        plot_hooks_data = load_yaml('plot_hooks.yml').get('plot_hooks', [])

        if not settings_data or not plot_hooks_data or not character_sheet:
            print("Failed to load necessary data from YAML files.")
            exit(1)
        print('building random setting doc')
        setting_doc = ''.join(random.choice(settings_data)) + ''.join(random.choice(plot_hooks_data))
        # setting_doc = random.choice(settings_data) + random.choice(plot_hooks_data)
 	
    

    if len(responses) == 0:

        context = [
            {'name': 'system instructions', 'role': 'system', 'content': general_instructions},            
            {'name': 'setting document', 'role': 'system', 'content': f"Setting Document--{setting_doc}"},
            {'name': 'character sheet 1', 'role': 'system', 'content': f"Character Sheet--{character_sheet}"},
            {'name': 'initial instruction', 'role': 'system', 'content': initial_instruction}
        ]
    else:
        
        context = [
            {'name': 'system instructions', 'role': 'system', 'content': general_instructions},
        	{'name': 'setting document', 'role': 'system', 'content': f"Setting Document--{setting_doc}"},
            {'name': 'character sheet 1', 'role': 'system', 'content': f"Character Sheet 1--{character_sheet}"}
        ] + responses
    context.append({'name': 'continue instruction', 'role': 'system', 'content': continue_instruction})
    return context

def build_raw_template(context):
    template = """
{% for item in context %}
- name: {{ item.name | tojson }}
  role: {{ item.role | tojson }}
  content: |
    {{ item.content | tojson }}
{% endfor %}
    """
    jinja_template = Template(template)
    return jinja_template.render(context=context)

model = ChatOpenAI(model="gpt-4o-mini")

while True:
    print('~~~~~~~~~~~~~~~~~~~~~~~')
    try:
        context = build_context(setting_doc, character_sheet)

        raw_template = build_raw_template(context)

        # Ensure the raw_template is not None or empty
        if not raw_template:
            print("Raw template is empty or None")
            break

        # Prepare the template data
        template_data = {
            "setting_doc": setting_doc,
            "character_sheet": character_sheet
        }

        # Create the prompt with the current context
        try:
            prompt = Prompt(
                raw_template=raw_template,
                template_data=template_data
            )
        except Exception as e:
            print(f"Error creating Prompt object: {e}")
            break

        try:
            response = model.invoke(prompt.messages)
            print(f"DM: {response.content}")

            # Append the new response to the responses list and context
            response_entry = {
                'name': 'response',
                'role': 'assistant',
                'content': response.content
            }
            responses.append(response_entry)
        except Exception as e:
            print(f"Error invoking model: {e}")
            break

        # Save the updated responses to responses.yml
        try:
            with open(responses_path, 'w') as file:
                yaml.safe_dump(responses, file)
        except Exception as e:
            print(f"Error saving responses to file: {e}")
            break

        # Get the next user input
        user_input = input("Your turn: ")

        # Append the user input to the context
        user_entry = {
            'name': 'user',
            'role': 'user',
            'content': user_input
        }
        responses.append(user_entry)

    except Exception as e:
        print(f"Error: {e}")
        break
