# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai

openai.organization = "org-6b0b0e0e-1b5a-4b0e-9f9a-9c1b2b5c6d7e"
openai.api_key =

openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    ]
)
