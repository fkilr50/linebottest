from flask import Flask, request, jsonify
from qa_model import answer_question  # Import the function from qa_model.py

app = Flask(__name__)

# Function to get dynamic context (e.g., sustainability or study-related information)
def get_dynamic_context():
    """
    This function returns a broader context which can be dynamically modified 
    or fetched from a live data source (e.g., news, API, etc.).
    """
    context = """
    Renewable energy sources include solar, wind, hydroelectric, geothermal, and biomass energy.
    Climate change refers to the long-term change in Earth's climate patterns, mainly due to human activities.
    Sustainability involves meeting the needs of the present without compromising the ability of future generations to meet their own needs.
    Effective study methods include active recall, spaced repetition, and regular breaks.
    For example, using flashcards and summarizing notes can help retain information.
    """
    return context

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    This endpoint receives the user's message and sends it to the model 
    for a dynamic answer based on the context.
    """
    data = request.get_json()
    user_input = data['events'][0]['message']['text'].lower()  # Get the user input and convert to lowercase

    # Default response if no answer is found
    response_message = "I'm not sure what you're asking for."

    # Get dynamic context (can be extended with live data)
    context = get_dynamic_context()

    # Pass the user's question and context to Hugging Face model
    response_message = answer_question(user_input, context)
    
    return jsonify({'reply': response_message})

if __name__ == '__main__':
    app.run(debug=True)
