import os
from openai import OpenAI # type: ignore
client = OpenAI()

# completion = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[
#         {
#             "role": "user",
#             "content": "Write a one-sentence bedtime story about a unicorn."
#         }
#     ]
# )

# print(completion.choices[0].message.content)

#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # type: ignore
def main():
    if not client:
        print("API key not found. Please set it in the OPENAI_API_KEY environment variable.")
        exit(1)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Specify the correct model
            messages=
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say this is a test."}
            ],
            #max_tokens=5,
            n=2,
            #temperature=0.7,
            #top_p=0.9
        )
        print(len(response.choices))
        #print(response.choices[0].message['content'].strip())
        first_response = response.choices[1].message.content
        print("First response:", first_response)

         # Access the second completion
        second_response = response.choices[0].message.content
        print("Second response:", second_response)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()