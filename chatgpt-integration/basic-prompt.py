import openai
import time


# Replace 'your-api-key' with your actual OpenAI API key
API_KEY = 'xxxx'

# Initialize the OpenAI API client
openai.api_key = API_KEY

def ask_question(question):
    retries = 3
    for i in range(retries):
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" for the latest ChatGPT model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question},
                ],
            )
            # Extract the text from the response
            answer = response.choices[0].message['content'].strip()
            return answer
        except openai._exceptions.RateLimitError as e:
            print(f"Rate limit exceeded. Retrying in {2 ** i} seconds...")
            time.sleep(2 ** i)
        except openai._exceptions.OpenAIError as e:
            print(f"OpenAI API error: {e}")
            break
    return "Sorry, I'm unable to process your request at the moment."

def main():
    while True:
        question = input("Ask a question (or type 'exit' to quit): ")
        if question.lower() == 'exit':
            break
        answer = ask_question(question)
        print("ChatGPT: {}".format(answer))

if __name__ == "__main__":
    main()