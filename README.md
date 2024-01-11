# StoryGarten
Now available as a GPT on OpenAI's GPT store! Find it [here](https://chat.openai.com/g/g-fQiOj22nE-storygarten)!
An assistant that uses the new OpenAI Assistant API to write children's books. Just a fun little project to experiment with the new assistant & threads API. Future plans include adding DALL-E integration to illustrate pages.


## Future additions
DALL-E integrations
  - include character descriptions for attempt at continuity
Rhyme scheme
Storybook style UI

## Examples
Example storyboards in JSON format can be found in the `storyboards` directory

## Setup/Installation Instructions

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Steps

1. Clone the repository to your local machine.
```
git clone https://github.com/martinr9315/storygarten.git
```
2. Navigate to the cloned repository.
```
cd storygarten
```
3. Install the required Python packages.
```
pip install -r requirements.txt
```
The `requirements.txt` file includes the necessary packages, namely PyQt5 and openai.
4. Run the `story_writer_gui.py` script to start the application.
```python3 story_writer_gui.py```

**Please note that you need to have OpenAI API keys set up in your environment to use the OpenAI functionalities.**


