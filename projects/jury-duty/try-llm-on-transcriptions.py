
# Use a pipeline as a high-level helper
from transformers import pipeline

messages = [
    {"role": "user", "content": "Who are you?"},
]
pipe = pipeline("text-generation", model="meta-llama/Llama-3.3-70B-Instruct")
pipe = pipeline("text-generation", model="meta-llama/Llama-3.2-3B-Instruct")
pipe(messages)

from transformers import pipeline

# Create a pipeline for a specific task
pipe = pipeline("question-answering")
context = 
question = "What date is jury duty?"
pipe({"question": question, "context": context})




# # Load model directly
# from transformers import AutoTokenizer, AutoModelForCausalLM

# tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
# model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")

# # Example transcription
# transcription = """
# """

# # What's the date of jury service in YYYY-MM-DD format?
# # Which groups are required to report?
# # Which groups aren't required to report?


# # Questions to ask
# questions = [
#     # "What is the jury service date? Answer only in YYYY-MM-DD form.",
#     "Which groups are required to report?"
#     # "Which groups do not need to report?"
#     # "Which groups do not need to report and their service is excused?"
# ]
# # Function to generate an answer
# def get_answer(question, context):
#     # Format the prompt for instruction-following
#     prompt = f"Given the following transcription:\n\n{context}\n\nAnswer this question: {question}"
#     input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    
#     # Generate response
#     output = model.generate(
#         input_ids,
#         # max_length=100,  # Adjust based on expected answer length + prompt
#         max_new_tokens=20,  # Limit the number of tokens generated
#         num_return_sequences=1,
#         do_sample=False,  # Greedy decoding for precise answers
#         temperature=0.1,  # Low temperature for factual responses
#         pad_token_id=tokenizer.eos_token_id  # Avoid warnings
#     )
    
#     # Decode and extract the answer
#     full_response = tokenizer.decode(output[0], skip_special_tokens=True)
#     answer = full_response[len(prompt):].strip()  # Remove prompt from response
#     return answer

# # Ask questions and print answers
# for question in questions:
#     answer = get_answer(question, transcription)
#     print(f"{question}: {answer}")

