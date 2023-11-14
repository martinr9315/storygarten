import tkinter as tk
from tkinter import simpledialog, messagebox
from openai import OpenAI
import time
import json
import uuid
import re


class StoryWriter:
    def __init__(self):
        self.client = OpenAI()
        self.assistant = self.create_assistant()
        self.thread = self.create_thread()
        self.last_message_id = None

    def create_assistant(self):
        print("Calling OpenAI...")
        return self.client.beta.assistants.create(
            name="Children's Author",
            instructions=("You are a creative, illustrated children's book author "
                          "renowned for explaining topics via simple stories. "
                          "Given a topic to focus on you will come up with a story "
                          "outline (characters, setting, bullet-pointed plot) that "
                          "exemplifies the desired topic. "
                          ),
            model="gpt-4-1106-preview"
        )

    def create_thread(self):
        print("Calling OpenAI...")
        return self.client.beta.threads.create()

    def create_message_and_run(self, role, content):
        print("Calling OpenAI...")
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role=role,
            content=content,
        )
        print("Calling OpenAI...")
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )
        self.wait_for_run_completion(run.id)
        return message, run

    def wait_for_run_completion(self, run_id):
        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run_id
            )
            if run.status == 'completed':
                break
            time.sleep(1)

    def get_thread_messages(self):
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )
        new_messages = []
        for d in messages.data:
            if self.last_message_id is None or d.id != self.last_message_id:
                new_messages.append(d)
            else:
                break
        message_string = ""
        for d in reversed(new_messages):
            if d.role == 'assistant':
                for c in d.content:
                    if c.type == 'text':
                        message_string += '\t' + c.text.value + "\n"
        if new_messages:
            self.last_message_id = messages.first_id
        return message_string


class StoryGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        self.root.title("Story Book")
        self.root.geometry("800x600")  # Set the size of the window
        self.root.configure(bg='saddle brown')  # Set the background color to resemble a book cover

        # Create a frame to resemble a book page
        self.page = tk.Frame(self.root, bg='ivory', bd=5)
        self.page.place(relx=0.5, rely=0.5, anchor='center')  # Place the frame at the center of the window

        # Create a text widget to display the story
        self.story_text = tk.Text(self.page, bg='ivory', fg='black', font=('Times', 12), wrap='word')
        self.story_text.pack(fill='both', expand=True)

        # Create a scrollbar for the text widget
        self.scrollbar = tk.Scrollbar(self.story_text)
        self.scrollbar.pack(side='right', fill='y')

        # Attach the scrollbar to the text widget
        self.story_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.story_text.yview)

        self.writer = StoryWriter()

    def get_user_input(self, prompt):
        return simpledialog.askstring("Input", prompt).lower()

    def satisfaction_loop(self, prompt, action):
        satisfaction = 'no'
        while satisfaction != 'yes':
            result = action()
            result_message = self.writer.get_thread_messages()
            messagebox.showinfo(prompt, result_message)
            satisfaction = self.get_user_input(f"Are you satisfied with the given {prompt}? (yes/no): ")
        return result_message

    def generate_story(self):
        topic = self.get_user_input("Please enter the topic for the story: ")
        audience = self.get_user_input("Please enter the target audience: ")
        outline_json = markdown_json_to_dict(self.satisfaction_loop("outline", lambda: self.writer.create_message_and_run("user", f"Please write a story outline explaining {topic} for {audience}. The output should be a JSON with field 'characters', 'setting', 'plot'.")))
        print(outline_json['characters'])
        # TODO: if satisfied with outline, need physical description of each character in the story to use for image generation. 
        story = self.satisfaction_loop("story", lambda: self.writer.create_message_and_run("user", "Please flesh out the outline to a full story"))
        storyboard = markdown_json_to_dict(self.satisfaction_loop("page breaks", lambda: self.writer.create_message_and_run("user", "Please break the story up into pages and suggest an accompanying illustration for each page in JSON format with the fields 'page_number', 'text', 'illustration'")))

        uid = uuid.uuid4()
        with open(f'./storyboards/{uid}.json', 'w') as f:
            json.dump(storyboard, f)

        return storyboard
    
    def load_storyboard(self, uid):
        with open(f'./storyboards/{uid}.json', 'r') as f:
            storyboard = json.load(f)
        return storyboard

# TODO: need backoff so api requests go thru, need style/character continuity thru images
    def generate_images(self, storyboard):
        pages = {}
        for i, page in enumerate(storyboard):
            description = page['illustration']
            response = self.writer.client.images.generate(
                model="dall-e-3",
                prompt=description,
                size="1024x1024",
                quality="standard",
                n=1,
                )
            image_url = response.data[0].url
            pages[i] = [description, image_url]
            print(description, image_url)
        return pages


def markdown_json_to_dict(markdown_str):
    # Assuming the JSON is in a code block, extract it
    # Adjust the regular expression according to your markdown format
    json_str = re.search(r'```json(.+?)```', markdown_str, re.DOTALL)
    if json_str:
        json_str = json_str.group(1).strip()
        return json.loads(json_str)
    else:
        raise ValueError("No JSON found in the markdown")


if __name__ == "__main__":
    gui = StoryGUI()
    pages = gui.generate_story()
    gui.root.mainloop()
    # storyboard = gui.load_storyboard("f9a3274a-ee80-41dd-a003-3bb3ea78ba51")
    # images = gui.generate_images(storyboard)
    # print(images)
    exit(0)
    