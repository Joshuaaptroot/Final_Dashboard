from flask import Flask, render_template_string
import openai

app = Flask(__name__)

def generate_commentary():
    client = openai.OpenAI(api_key='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')

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Specify the engine you want to use
        messages=[
            {"role": "system", "content": "you are a data analyst"},
            {"role": "user", "content": "pretend to find a correlation in a database"},
        ]
    )

    commentary = completion.choices[0].message

    return commentary

@app.route('/')
def render_main_html():

    with open('Main.html', 'r') as file:
        html_content = file.read()

    commentary = generate_commentary()

    modified_html = html_content.replace('<!-- COMMENTARY_PLACEHOLDER -->')