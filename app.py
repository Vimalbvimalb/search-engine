from flask import Flask, render_template_string, request, jsonify
import wolframalpha
import wikipedia

app = Flask(__name__)

# Initialize WolframAlpha client
client = wolframalpha.Client("8H7LLR-74UEEXQ9RW")

@app.route('/')
def home():
    # Inline HTML, CSS, and JavaScript code for a single-page application
    html_code = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RAVA AI Assistant - Ask your Questions</title>
        <style>
            /* Inline CSS for styling the page */
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background: white;
                padding: 20px;
                text-align: center;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            h1 {
                color: #333;
            }
            input[type="text"] {
                padding: 8px;
                width: 80%;
                margin-bottom: 10px;
                border-radius: 5px;
                border: 1px solid #ccc;
            }
            button {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                background-color: #28a745;
                color: white;
                cursor: pointer;
            }
            button:hover {
                background-color: #218838;
            }
            .result {
                margin-top: 20px;
                text-align: left;
            }
            .result h2 {
                font-size: 1.2em;
                color: #555;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>RAVA AI Assistant</h1>
            <p>Ask your Questions</p>
            <form id="query-form" onsubmit="return false;">
                <input type="text" id="query-input" placeholder="Enter a question" required>
                <button type="button" onclick="askQuestion()">Ask</button>
            </form>
            <div class="result" id="result">
                <h2>Results:</h2>
                <p id="wolfram-result"></p>
                <p id="wikipedia-result"></p>
            </div>
        </div>
        <script>
            // JavaScript for handling the query and displaying results
            async function askQuestion() {
                const query = document.getElementById('query-input').value;
                
                if (!query) {
                    alert('Please enter a query.');
                    return;
                }

                const response = await fetch('/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });

                const data = await response.json();
                const wolframResult = data.wolfram || "No result from WolframAlpha.";
                const wikipediaResult = data.wikipedia || "No result from Wikipedia.";

                document.getElementById('wolfram-result').innerText = "WolframAlpha: " + wolframResult;
                document.getElementById('wikipedia-result').innerText = "Wikipedia: " + wikipediaResult;

                speakResults(wolframResult, wikipediaResult);
            }

            function speakResults(wolframResult, wikipediaResult) {
                const msg = new SpeechSynthesisUtterance();
                msg.text = "WolframAlpha: " + wolframResult + ". Wikipedia: " + wikipediaResult;

                if ('speechSynthesis' in window) {
                    window.speechSynthesis.speak(msg);
                } else {
                    console.log("Speech synthesis not supported.");
                }
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_code)

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query = data['query']
    
    wolfram_res = None
    wiki_res = None

    try:
        # Query WolframAlpha
        res = client.query(query)
        wolfram_res = next(res.results).text
    except Exception as e:
        wolfram_res = f"Error: {str(e)}"

    try:
        # Query Wikipedia
        wiki_res = wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError:
        wiki_res = "The query returned multiple results, please be more specific."

    return jsonify(wolfram=wolfram_res, wikipedia=wiki_res)

if __name__ == '__main__':
    app.run(debug=True)
