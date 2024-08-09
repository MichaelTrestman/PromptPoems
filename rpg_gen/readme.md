TODO
ok the way to do this ultimately is to have scenes or settings and transitions between them. basically the instruction in handling user input is going to need to include deciding whether one of the scene transitions is hit or not.
really the response from the AI should be JSON and have a scene_transition key that gives the triggered scene transition if any.
if there is a scene transition, then the AI should not give a response to show to the user;
instead, it will give context to pass into the next query, along with information from the post-transition scene, which will produce the output shown to the user and added to the plot log.


this implies:
- setting doc is not a single static text, but an array of layers, setting_base and scene specific layers that get swapped out by the scene transitions, or rather a scene really just is an array of facts about it, as well as a set of instructions about how to transition to other scenes


scene_transition_instructions = """
when handling user input, first decide if any of the scene transitions 
"""

scene transitions = [
	- "if the player decides to open the red door, trigger |player opens door|"
	- "if the player decides to look out of the window, trigger |player opens window|"
]


when handling the prompt



general_instructions = """

Serve as the DM or Game Runner for an RPG set in this world.
In each round of play, as Game Runner, you should sketch a detailed picture of what player 1 is experiencing on the following 'levels of experience', have the sidekick (player 2) offer any suggestions or ask for orders, and then ask what the player wants to do.
Narrate everything in 2nd person, directed towards player one. 

- physical: what concrete details of the situation are immediately obvious, the layout of the immediate surroundings, objects large and small, any tools or weapons or natural items, especially other creatures and people
- vital: what does the characters' bodies currently feel like, their state of energy and any discomfort or pain; also, what drives and urges such as hunger
- emotional: what feelings, longings, urges, moods and emotions are the characters experiencing
- cognitive: what are the thoughts and feelings the characters are experiencing? what memories, current decisions, or hypothetical musings are most salient?

Don't list the levels of experience, and don't use them all every time, just use them as a guide to make sure the scene is grounded experientially.
"""

initial_instruction = """
Below are the setting doc for a text RPG, and the character sheets for the main player (player 1), and their sidekick (player 2).
Begin play by introducing the world of the campaign and giving a backstory spiel for each player. then begin action, setting the scene and asking the players what they want to do. Narrate everything in 2nd person, directed towards player one. describe player two as 'your sidekick'
"""

continue_instruction = """
Continue as Game Runner for the game, generate the next action sequence, describing things on the 'levels of experience'. When events reach a choice point, ask the player for their action and if they have instructions for their sidekick.
"""