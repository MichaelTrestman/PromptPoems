import os
import yaml
import random
from prompt_poet import Prompt
from langchain_openai import ChatOpenAI

# Uncomment if you need to set OPENAI_API_KEY.
# os.environ["OPENAI_API_KEY"] =

# Define the setting documents and character sheets
setting_docs = [
    'In a world where gravity is unpredictable and fluctuates wildly, cities are built on giant floating platforms that drift across the sky. Society revolves around "gravity smiths" who can temporarily stabilize gravity fields. The constant motion of the platforms creates a nomadic lifestyle where resources are scarce and innovation is key.',
    'The world is dominated by colossal fungal forests that spread spores everywhere, creating a hallucinogenic environment. Civilization exists in massive biodomes to protect against the spore influence. However, certain factions worship the fungi and live outside the domes, seeking to merge with the forest consciousness.',
    'A post-apocalyptic desert wasteland where technology and magic have fused. The remnants of humanity survive in scattered oasis cities powered by ancient tech-magic reactors. Warlords and sorcerers battle for control of the scarce resources, while mysterious desert spirits influence events.',
    'A world covered entirely in dense jungle, with cities built in the treetops. The ground is overrun by dangerous, hyper-evolved predators, so humans live among the canopy. The society is tribal, and the "Sky Rangers" are elite warriors who protect the tree cities and explore the deadly ground below.',
    'In a steampunk Victorian-era city powered by steam and clockwork technology, an eternal fog blankets the streets. Strange creatures lurk in the mist, and the city is divided into the elite who live in towering spires above the fog, and the underclass who dwell in the perpetual gloom below.'
]

plot_hooks = [
    'A mysterious signal is detected from an abandoned research facility.',
    'An ancient artifact with unknown powers is uncovered.',
    'A powerful storm is approaching, threatening the stability of the floating platforms.',
    'A faction leader goes missing under suspicious circumstances.',
    'A strange illness starts spreading among the inhabitants.'
]

character_sheets = [
    'Zog the Unyielding the Cybernetic Barbarian; Special trait: Has a mechanical arm with interchangeable tools and weapons, and a body covered in glowing tribal tattoos that enhance his strength.',
    'Lady Seraphina the Quantum Sorceress; Special trait: Wears a flowing robe made of starlight and can manipulate time and space, but is haunted by visions of alternate realities.',
    'Torque Wrench the Steam Engineer; Special trait: A genius inventor with a monocle that doubles as a targeting system, and carries an arsenal of self-built gadgets and gizmos.',
    'Whisper the Shadow Assassin; Special trait: Moves silently through the fog, can become invisible in shadows, and has a pet raven that spies on enemies and brings back information.',
    'Dr. Fungus the Myco-Knight; Special trait: Armored in living fungal armor that regenerates and heals him, and can control the growth of fungi to create barriers or launch spore attacks.'
]

# Randomly select a setting document and two character sheets
selected_setting_doc = random.choice(setting_docs)
selected_character_sheets = random.sample(character_sheets, 2)
character_sheet_1 = selected_character_sheets[0]
character_sheet_2 = selected_character_sheets[1]

# Ensure character sheets are properly escaped
character_sheet_1 = character_sheet_1.replace('\n', '\\n').replace(':', '\\:')
character_sheet_2 = character_sheet_2.replace('\n', '\\n').replace(':', '\\:')

raw_template = """
- name: system instructions
  role: system
  content: |
    Below are the setting doc for an RPG and the character sheets for two players. Serve as the DM for an RPG set in this world. First generate a brief campaign summary then begin play.
    In each round of play, as Game Runner, you should sketch a detailed picture of what the characters are experiencing on the following 'levels of experience', and then ask what the characters plan to do.

    - physical: what concrete details of the situation are immediately obvious, the layout of the immediate surroundings, objects large and small, any tools or weapons or natural items, especially other creatures and people
    - vital: what does the characters' bodies currently feel like, their state of energy and any discomfort or pain; also, what drives and urges such as hunger
    - emotional: what feelings, longings, urges, moods and emotions are the characters experiencing
    - cognitive: what are the thoughts and feelings the characters are experiencing? what memories, current decisions, or hypothetical musings are most salient?
    As Game Runner, on each turn you should describe how the action proceeds until an important decision faces the characters, when you should present the decision to the players. Please roll checks and saves (using a pseudorandom process to generate fair rolls) for the characters but tell the players what the rolls are.
    Begin play by setting the scene and asking the players what they want to do. Alternate turns between the two players, narrating the action in between.
- name: setting document
  role: system
  content: "Setting Document--{{ setting_doc }}"
- name: plot hook
  role: system
  content: "Plot Hook--{{ plot_hook }}"
- name: character sheet 1
  role: system
  content: "Character Sheet 1--{{ character_sheet_1 }}"
- name: character sheet 2
  role: system
  content: "Character Sheet 2--{{ character_sheet_2 }}"
  
"""

template_data = {
  "setting_doc": selected_setting_doc,
  "character_sheet_1": character_sheet_1,
  "character_sheet_2": character_sheet_2
}

# Render the template to check for issues
from jinja2 import Template

template = Template(raw_template)
rendered_template = template.render(template_data)


# Validate the rendered template with a YAML parser
try:
    loaded_yaml = yaml.load(rendered_template, Loader=yaml.SafeLoader)
    print("YAML loaded successfully:")
    print(loaded_yaml)
except yaml.YAMLError as exc:
    print(f"YAML error: {exc}")

prompt = Prompt(
    raw_template=raw_template,
    template_data=template_data
)

model = ChatOpenAI(model="gpt-4o-mini")
    
try:
    response = model.invoke(prompt.messages)
    print(response.content)
    
    response_entry = {
        'name': 'response',
        'role': 'user',
        'content': response.content 
    }

    responses_path = 'responses.yml'
    
    if os.path.exists(responses_path):
        with open(responses_path, 'r') as file:
            responses = yaml.safe_load(file) or []
    else:
        responses = []

    responses.append(response_entry)
    
    for response in responses:
        print(f"Response from {response['role']}: {response['content']}")

    with open(responses_path, 'w') as file:
        yaml.safe_dump(responses, file)
    print("Response successfully written to responses.yml")

except Exception as e:
    print(f"Error: {e}")
