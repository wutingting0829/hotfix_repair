import openai
from dotenv import find_dotenv, load_dotenv
import os
import time
import logging
from datetime import datetime

# It is used to load environment variables from a .env file into the environment.
load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY") #I alredy set this in the .env file
client = openai.OpenAI()
model = "gpt-4o"

# ==  Create our Assistant (Uncomment this to create your assistant) ==
personal_trainer_assis = client.beta.assistants.create(
    name="Personal Trainer Assistant",
    instructions="I am your personal trainer assistant. I can help you with your workout routine, diet plan, and fitness goals.",
    model=model
)

print(personal_trainer_assis.id)


# === Thread (uncomment this to create your Thread) ===
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "Welcome to the Personal Trainer Assistant! How can I help you today?"
        }
    ]
)
print(thread.id)

# === Hardcode our ids ===
asistant_id = "asst_ArjM1l5qbZb0JSRFWTe1Z8PK"
thread_id = "thread_lB3f3BMkxnGu3uOa0YYJP93b"


# ==== Create a Message ====
message = "How many reps do I need to do to build lean muscles?"
message = client.beta.threads.messages.create(thread_id=thread_id, role="user", content=message)
print(message.id)

# === Run our Assistant ===
run = client.beta.threads.runs.create(thread_id=thread_id,  assistant_id=asistant_id,instructions="Please address the user as James Bond.", model=model)
print(run.id)


def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    """

    Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)


# === Run ===
wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)

# ==== Steps --- Logs ==
run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
print(f"Steps---> {run_steps.data[0]}")