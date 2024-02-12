# Import necessary modules and libraries. For this project, a range of libraries were needed due to the multi-functionality of the project.
from flask import Flask, jsonify, render_template, Response, abort, make_response, request #imports for the base flask application, and for improving security of the application
from cryptography.fernet import Fernet #fernet used for encryption
import openai # an OpenAI library used for methods relating to it's api. This was used to generate a completion for data commentary 
import sqlite3 #used to import methods relating to the SQLite database
import pathlib # used to provide the working directory
import logging # used to generate information and error logs
from flask_cors import CORS # used to allow access to the variable URL routes for all data.

#at this point I established the application
app = Flask(__name__)

# Define the absolute path of the working directory using the pathlib library
working_directory = pathlib.Path(__file__).parent.absolute()

# Define the path to the SQLite database file
DATABASE = working_directory / 'PData.db'

''' Enable CORS (Cross-Origin Resource Sharing) for the Flask app, this particular CORS onfiguration is insecure, as the origins are not specified and instead use a wildcard
This opens up the application to potential XSS attacks, where an attacker could execute a script in my browers through the data sent to the application. 
in a future, sprint, I would configure the CORS policy more carefully and specify the origin more clearly, as it is this could not be used in production
'''
CORS(app)
cors = CORS(app, resources={r"/api/ChartData/*": {"origins": "*"}})

# Configure logging to write logs to a file named 'app.log'
logging.basicConfig(filename="app.log", level=logging.DEBUG)

# yusing impored fernet functions, these lines generate a fernet key to be used in data encryption.
fernet_key = Fernet.generate_key()
cipher_suite = Fernet(fernet_key)

# this function encrypts an argument passed into it using, the uniform transformation format. this function is later used specifically on the AI out put, as this will be
def encrypt_data(data):
    return cipher_suite.encrypt(data.encode('utf-8'))

# Function to query the SQLite database, this later used to pull specific data.
def query_db(query: str, args=()) -> list:
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, args).fetchall()
    return result


''' Global variables to store x and y values as strings, whilst the use of global variables would make it hartder to build upon the application, especially in the context of a Development team,
this was a necessary addition in order to ensure data was passd between functions, and allow for, what is essentially, multiple returned values in the chart_data function, following these
initalisations. These global variables are later used as arguments in the AI genenration function.'''

global_x_values_str = ""
global_y_values_str = ""

# Route to fetch chart data based on user-selected x and y axes, in the JS file, the URL is defined in the fetch statements, which can now be used to guide our query to the database.
@app.route("/api/ChartData/<x_axis>/<y_axis>")
def chart_data(x_axis, y_axis) -> Response:
    global global_x_values_str, global_y_values_str

    # SQL query to retrieve data from the SQLite database, this varies based on the URL, the use of an 'f-string' here to allow for variable inputs is a simple but effective solution. 
    query = f"""
    SELECT {x_axis}, {y_axis}
    FROM RobotMetrics
    ORDER BY {x_axis}
    """
    try:
        # Execute the query and retrieve the result using the previously defined query_db function.
        result = query_db(query)

        '''Extract x and y values from the result, these values are extracted for use within the chart.
        the variables are set as the function loops over the ros within the result variable, and pulls the value at index 0 or 1 depending on axis'''
        x_values = [row[0] for row in result]
        y_values = [row[1] for row in result]

        '''Convert x and y values to comma-separated strings, the global variables are defined to be used in content generation functions.
        the .join() method concanates the values in the x_values and y_values, and the map() function takes the str function an applies it to the iterable values. '''
        global_x_values_str = ",".join(map(str, x_values))
        global_y_values_str = ",".join(map(str, y_values))

        # These lines simply Jsonify the data, allowing for easy navigation through the data when passing into either the AI generation or chart generation
        data = [{x_axis: row[0], y_axis: row[1]} for row in result]
        response = jsonify(data)

        # Renders the main HTML template through the application
        render_main_html()

        return response
    except sqlite3.Error as e:
        # Handle database errors and log the details to app.log
        logging.error("Database error: %s", e)
        abort(500, description="Database error has occurred, the data cannot be pulled for some reason???")

'''Function to generate AI commentary using OpenAI GPT-3. the function takes 4 arguments, 
the data for x and y axis and the column headers (whcih are defined in the following function: generate_Commentary_route'''
def generate_commentary_function(x, y, columnX, columnY):
    # Initialize the OpenAI GPT-3 client and save the API key to a variable. before going into production this key should be hidden in a secure evnironment and called to this variable. 
    client = openai.OpenAI(api_key='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')

    # Create a chat completion request to GPT-3,
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "you are a data analyst"},
            {"role": "user", "content": f"analyze the data with x-axis: {x} , y-axis: {y}, do not plot the values. the column header for x axis is: {columnX} and for yaxis is {columnY} simply make some judgments about whether there is a correlation, and mention what the column headers are. limit words to 200. do not refernece this input in your answer, as your completion will be presented as an isolated analysis of a table."},
        ]
    )

    # Extract the generated commentary from the GPT-3 response
    commentary = completion.choices[0].message.content
    encrypted_commentary = encrypt_data(completion.choices[0].message.content)
    
    # Log the encrypted_commentary, esnruing that no information passed by AI can be exploited in the .log files, which could be insecure. 
    logging.info(f"Chat Completion Result: {encrypted_commentary}")

    # Return the commentary as a JSON response for easy navigation.
    return jsonify({'result': commentary})


''' here we establish the second route for the Ai data to be established. Moreover, the URL information is used to inform the AI application of the column headers, 
giving insight into what the data relates to. here the function generate_commentary_function() is called and all the relevant variables are passed in'''
@app.route("/ai/<x_axis>/<y_axis>")
def generate_commentary_route(x_axis, y_axis):
    commentary = generate_commentary_function(global_x_values_str, global_y_values_str, x_axis, y_axis)
    return commentary

'''in order to to edit the HTML with the chat completion, a second .html file was created named modified.html.
this function, copies the HTML from main.html and writes it with the new commentary to the modified version. giving the effect that the interface changes'''
def render_main_html():
    # Read the contents of the main HTML template
    with open('Templates/Main.html', 'r') as file:
        html_content = file.read()

    # Generate AI commentary and replace a placeholder in the HTML template
    commentary = generate_commentary_function(global_x_values_str, global_y_values_str, "Null", "Null")
    modified_html = html_content.replace('<!-- COMMENTARY_PLACEHOLDER -->', str(commentary))

    # Write the modified HTML to a file
    with open('Templates/modified.html', 'w') as file:
        file.write(modified_html)

# Route for the main page, in this case it is the modified HTML, as this contains the completion
@app.route('/')
def index() -> str:
    # Render the main HTML template with modified commentary
    modified_html = render_main_html()
    return render_template('modified.html', modified_html=modified_html)

# Define error handlers for 404 (Not Found) and 500 (Internal Server Error)
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({"error": "Internal server error"}), 500)


# Run the Flask app if the script is executed
if __name__ == '__main__':
    app.run(debug=True)

