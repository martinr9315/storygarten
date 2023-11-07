from openai import OpenAI
import time
import json
import uuid


class StoryWriter:
    def __init__(self):
        self.client = OpenAI()
        self.assistant = self.create_assistant()
        self.thread = self.create_thread()
        self.last_message_id = None

    def create_assistant(self):
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
        return self.client.beta.threads.create()

    def create_message_and_run(self, role, content):
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role=role,
            content=content,
        )
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

    def get_user_input(self, prompt):
        return input(prompt).lower()

    def generate_story(self):
        topic = self.get_user_input("Please enter the topic for the story: ")
        audience = self.get_user_input("Please enter the target audience: ")

        satisfaction = 'no'
        while satisfaction != 'yes':
            self.create_message_and_run("user", "Please write a story outline explaining "+topic+" for "+audience)
            outline = self.get_thread_messages()
            print(outline)
            satisfaction = self.get_user_input("Are you satisfied with the given outline? (yes/no): ")

        satisfaction = 'no'
        while satisfaction != 'yes':
            self.create_message_and_run("user", "Please flesh out the outline to a full story")
            story = self.get_thread_messages()
            print(story)
            satisfaction = self.get_user_input("Are you satisfied with the given story? (yes/no): ")

        storyboard = {}
        satisfaction = 'no'
        while satisfaction != 'yes':
            self.create_message_and_run("user", "Please break the story up into pages and suggest an accompanying illustration for each page in JSON format with the fields 'page_number', 'text', 'illustration'.")
            storyboard = self.get_thread_messages()
            uid = uuid.uuid4()
            with open(f'./storyboards/{uid}.json', 'w') as f:
                json.dump(storyboard, f)
            satisfaction = self.get_user_input("Are you satisfied with the given page breaks? (yes/no): ")
        return storyboard

    def generate_images(self, pages):
        images = []
        for page in pages:
            description = page['illustration']
            image = self.client.images.generate(description=description)
            images.append(image)
        return images


if __name__ == "__main__":
    writer = StoryWriter()
    pages = writer.generate_story()