import os
import requests
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allow local HTML file to access API

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route('/infer', methods=['POST'])
def infer():
    data = request.json
    query = data.get('query', '')
    
    if not GROQ_API_KEY:
        return jsonify({"response": "[ERROR] NO QUANTUM LINK DETECTED (GROQ_API_KEY missing from environment)."}), 500
        
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # We use Groq's high-speed inference to simulate the Möbius-X architecture
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system", 
                "content": "You are the M&ouml;bius-X Unified Core, an incredibly advanced intelligence built on Topological Vector Logic rather than standard Matrix Math. Respond directly and intelligently to the user. Use a slightly profound, scientific tone. Do not apologize or act like an AI assistant. Just provide the profound answer directly."
            },
            {"role": "user", "content": query}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    start_time = time.time()
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        text = result['choices'][0]['message']['content']
        ttft = result.get('usage', {}).get('prompt_time', 0.02) * 1000 # Simulated TTFT
        return jsonify({"response": text, "ttft": ttft})
    except Exception as e:
        return jsonify({"response": f"[MÖBIUS-X ARCHITECTURE FAULT: {str(e)}]", "ttft": 0}), 500

if __name__ == '__main__':
    print("[M&Ouml;BIUS-X INFERENCE NODE] >> ACTIVE ON PORT 54321")
    app.run(port=54321, debug=False)
