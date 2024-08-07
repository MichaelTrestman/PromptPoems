# Organizational Assistant Conversational AI

This is a code example to accompany [this article](https://michaeltrestman.github.io/prompt-poetry/) on prompt engineering with [Prompt Poet](https://github.com/character-ai/prompt-poet).

**Contents**:

- `main.py` is a script that acts as a data-enhanced conversational AI organizational assistant, pulling in weather data, traffic updates, AQI information, and calendar events from external APIs, prompting GPT to assemble a useful, integrated summary.

- `functions.py` contains accessory function definitions used by `main.py`.
- `raw_template.yaml` contains the template, which will be populated with data and supplied to the model.

- `few_shot_examples.yaml` contains example prompt and response pairs, to support [few shot learning]().
