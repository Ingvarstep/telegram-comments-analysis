from tqdm import tqdm 
import openai
import json
import re

system = """Please analyze comments written in Ukrainian and extract the following fields where possible:

Which city, add oblast (e.g., "Чернігівська область") for disambiguation,  school, which type of digital school journal is used, how often teachers used it (variants: "завжди", "періодично", "рідко", "ніколи"), sentiment (variants: "нейтральний", "позитивний", "негативний"). If a comment is unrelated to a question about the digital school journal, write "-" symbol. 

Example: 
"
+
м. Ірпінь
ЗОШ№1
Нові знання

Дуже подобається наявність такого продукту. Він не ідеальний, але краще ніж нічого. Але маю як негативний так і позитивний досвід. 
"

Output:
city: Ірпінь | oblast: Київська | school: ЗОШ №1 | type: - | usage: - | sentiment: нейтральний
"""


openai.api_key = input()

def get_chatgpt(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
         messages=messages
        )
    return response

def analyze_comment(comment: str):
    messages = [
        {'role': 'system', 'content': system},
        {'role': 'user', 'content': comment}
    ]
    response = get_chatgpt(messages)['choices'][0]['message']['content']
    return response

def analyze_comments(comments: list):
    responses = []
    for comment in tqdm(comments):
        response = analyze_comment(comment)
        responses.append(response)
    return responses

if __name__ == '__main__':
    with open('data/messages.json', 'r') as f:
        comments = json.load(f)['messages']

    responses = analyze_comments(comments)

    with open('data/responses.json', 'w') as f:
        json.dump({'responses': responses}, f)