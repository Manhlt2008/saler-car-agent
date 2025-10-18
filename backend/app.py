import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import config

app = Flask(__name__)
CORS(app)

client = OpenAI(
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

modelName = os.getenv("AZURE_DEPLOYMENT_NAME")


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        response = client.chat.completions.create(
            model=modelName,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        assistant_message = response.choices[0].message.content

        return jsonify({
            'response': assistant_message
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3004, debug=True)
