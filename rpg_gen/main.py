import os
import yaml
import random
import logging
from prompt_poet import Prompt
from langchain_openai import ChatOpenAI
from jinja2 import Template

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Uncomment if you need to set OPENAI_API_KEY.
# os.environ["OPENAI_API_KEY"] =

# Load settings, plot hooks, and character sheets from YAML files
def load_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Error loading YAML file {file_path}: {e}")
        return {}

settings_data = load_yaml('settings.yml').get('settings', [])
plot_hooks_data = load_yaml('plot_hooks.yml').get('plot_hooks', [])
character_sheets_data = load_yaml('character_sheets.yml').get('character_sheets', [])

# Check if data is loaded correctly
if not settings_data or not plot_hooks_data or not character_sheets_data:
    logging.error("Failed to load necessary data from YAML files.")
    exit(1)

# Randomly select a setting document and two character sheets
selected_setting_doc = random.choice(settings_data)
selected_plot_hook = random.choice(plot_hooks_data)
selected_character_sheets = random.sample(character_sheets_data, 2)
character_sheet_1 = selected_character_sheets[0]
character_sheet_2 = selected_character_sheets[1]

logging.debug(f"Selected setting document: {selected_setting_doc}")
logging.debug(f"Selected plot hook: {selected_plot_hook}")
logging.debug(f"Selected character sheets: {character_sheet_1}, {character_sheet_2}")

# Function to ensure content is properly formatted for YAML
def format_for_yaml(content):
    return yaml.dump(content, default_flow_style=False).strip()

general_instructions = """
Below are the setting doc for an RPG and the character sheets for two players. Serve as the DM for an RPG set in this world. First generate a brief campaign summary then begin play.
In each round of play, as Game Runner, you should sketch a detailed picture of what the characters are experiencing on the following 'levels of experience', and then ask what the characters plan to do.

- physical: what concrete details of the situation are immediately obvious, the layout of the immediate surroundings, objects large and small, any tools or weapons or natural items, especially other creatures and people
- vital: what does the characters' bodies currently feel like, their state of energy and any discomfort or pain; also, what drives and urges such as hunger
- emotional: what feelings, longings, urges, moods and emotions are the characters experiencing
- cognitive: what are the thoughts and feelings the characters are experiencing? what memories, current decisions, or hypothetical musings are most salient?
"""

initial_instruction = """
Begin play by setting the scene and asking the players what they want to do. Alternate turns between the two players, narrating the action in between.
"""

continue_instruction = """
Continue as Game Runner for the game, as instructed. After each turn generate action until a choice point and then ask the player for their next turn.
"""

responses_path = 'responses.yml'

if os.path.exists(responses_path):
    try:
        with open(responses_path, 'r') as file:
            responses = yaml.safe_load(file) or []
    except Exception as e:
        logging.error(f"Error loading responses from {responses_path}: {e}")
        responses = []
else:
    responses = []

def build_context():
    if len(responses) == 0:
        context = [
            {'name': 'system instructions', 'role': 'system', 'content': general_instructions},
            {'name': 'initial instruction', 'role': 'system', 'content': initial_instruction},
            {'name': 'setting document', 'role': 'system', 'content': f"Setting Document--{selected_setting_doc}"},
            {'name': 'plot hook', 'role': 'system', 'content': f"Plot Hook--{selected_plot_hook}"},
            {'name': 'character sheet 1', 'role': 'system', 'content': f"Character Sheet 1--{character_sheet_1}"},
            {'name': 'character sheet 2', 'role': 'system', 'content': f"Character Sheet 2--{character_sheet_2}"}
        ]
    else:
        context = responses + [{'name': 'continue instruction', 'role': 'system', 'content': continue_instruction}]
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
    try:
        context = build_context()
        logging.debug(f"Context: {context}")

        raw_template = build_raw_template(context)
        logging.debug(f"Raw template: {raw_template}")

        # Ensure the raw_template is not None or empty
        if not raw_template:
            logging.error("Raw template is empty or None")
            break

        # Prepare the template data
        template_data = {
            "setting_doc": selected_setting_doc,
            "plot_hook": selected_plot_hook,
            "character_sheet_1": character_sheet_1,
            "character_sheet_2": character_sheet_2
        }

        # Create the prompt with the current context
        try:
            prompt = Prompt(
                raw_template=raw_template,
                template_data=template_data
            )
            logging.debug(f"Prompt created successfully: {prompt.messages}")
        except Exception as e:
            logging.error(f"Error creating Prompt object: {e}")
            break

        # Log the prompt details
        logging.debug(f"Prompt messages: {prompt.messages}")

        try:
            response = model.invoke(prompt.messages)
            logging.debug(f"Response: {response.content}")
            print(f"DM: {response.content}")

            # Append the new response to the responses list and context
            response_entry = {
                'name': 'response',
                'role': 'assistant',
                'content': response.content
            }
            responses.append(response_entry)
        except Exception as e:
            logging.error(f"Error invoking model: {e}")
            break

        # Save the updated responses to responses.yml
        try:
            with open(responses_path, 'w') as file:
                yaml.safe_dump(responses, file)
            logging.info("Response successfully written to responses.yml")
        except Exception as e:
            logging.error(f"Error saving responses to file: {e}")
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
        logging.error(f"Error: {e}")
        break
