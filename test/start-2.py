import ollama

#1 Generate a response from prompt 
res = ollama.generate(
    model="llama3.2",
    prompt="Why is the sky blue? (short answer)"
)

print("Answer: ", res["response"])


#2 Chat with the model in a stream fashion
res = ollama.chat(
    model="llama3.2",
    messages=[
        {"role": "user", "content": "What is the meaning of life?"},
    ],
    stream=True,
)

for chunk in res:
    print(chunk["message"]["content"], end="", flush=True)


#3 Create a model file with in-line model definition

'''
model_file = """
FROM llama3.2
SYSTEM You are a smart assitant who is very knowledgeable about stoicism. You are very pragmatic.
PARAMETER temperature 0.1
"""

ollama.create(model="stoic", modelfile=model_file, )

res = ollama.generate(
    model="stoic",
    prompt="What is the meaning of life? (short answer)"
)

print(res["response"])
'''