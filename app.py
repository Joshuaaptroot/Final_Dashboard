from flask import Flask, jsonify, render_template, Response, abort, make_response, render_template_string, request
from cryptography.fernet import Fernet
import openai
import sqlite3
import pathlib
import logging
from flask_cors import CORS

app = Flask(__name__)   
working_directory = pathlib.Path(__file__).parent.absolute()
DATABASE = working_directory / 'PData.db'
CORS(app)
cors = CORS(app, resources={r"/api/ChartData/*": {"origins": "*"}})

logging.basicConfig(filename="app.log", level=logging.DEBUG)
fernet_key = Fernet.generate_key()
cipher_suite = Fernet(fernet_key)

def encrypt_data(data):
    return cipher_suite.encrypt(data.encode('utf-8'))

def query_db(query: str, args=()) -> list:
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, args).fetchall()
    return result

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({"error": "Internal server error"}), 500)

global_x_values_str = ""
global_y_values_str = ""

@app.route("/api/ChartData/<x_axis>/<y_axis>")
def chart_data(x_axis, y_axis) -> Response:
    global global_x_values_str, global_y_values_str

    query = f"""
    SELECT {x_axis}, {y_axis}
    FROM RobotMetrics
    ORDER BY {x_axis}
    """
    try:
        result = query_db(query)

        x_values = [row[0] for row in result]
        y_values = [row[1] for row in result]

        global_x_values_str = ",".join(map(str, x_values))
        global_y_values_str = ",".join(map(str, y_values))

        data = [{x_axis: row[0], y_axis: row[1]} for row in result]
        response = jsonify(data)
        render_main_html()
        return response
    except sqlite3.Error as e:
        logging.error("Database error: %s", e)
        abort(500, description="Database error has occurred, the data cannot be pulled for some reason???")

@app.route("/ai/<x_axis>/<y_axis>")
def generate_commentary_route(x_axis, y_axis):
    commentary = generate_commentary_function(global_x_values_str, global_y_values_str, x_axis, y_axis)
    return commentary

def generate_commentary_function(x, y, columnX, columnY):
    client = openai.OpenAI(api_key='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')

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "you are a data analyst"},
            {"role": "user", "content": f"analyze the data with x-axis: {x} , y-axis: {y}, do not plot the values. the column header for x axis is: {columnX} and for yaxis is {columnY} simply make some judgments about whether there is a correlation, and mention what the column headers are."},
        ]
    )

    commentary = completion.choices[0].message.content
    encrypted_commentary = encrypt_data(completion.choices[0].message.content)
    logging.info(f"Chat Completion Result: {commentary}")

    return jsonify({'result': commentary})

def render_main_html():
    with open('Templates/Main.html', 'r') as file:
        html_content = file.read()

    commentary = generate_commentary_function(global_x_values_str, global_y_values_str, "Null", "Null")
    modified_html = html_content.replace('<!-- COMMENTARY_PLACEHOLDER -->', str(commentary))

    with open('Templates/modified.html', 'w') as file:
        file.write(modified_html)

@app.route('/')
def index() -> str:
    modified_html = render_main_html()
    return render_template('modified.html', modified_html=modified_html)

if __name__ == '__main__':
    app.run(debug=True)
