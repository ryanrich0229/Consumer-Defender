import os
import json
import anthropic
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')
client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

@app.route('/')
def index():
    return send_from_directory('.', 'consumer-defender.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    estimate_text = data.get('estimate_text', '')
    vehicle_info = data.get('vehicle_info', '')

    if not estimate_text:
        return jsonify({'error': 'No estimate text provided'}), 400

    prompt = f"""You are Consumer Defender's Car Repair Defense AI. A customer has uploaded a repair estimate and needs you to analyze it for overcharges and unnecessary work.

Vehicle: {vehicle_info}

REPAIR ESTIMATE:
{estimate_text}

Analyze every line item against standard labor rates and parts costs. Return ONLY a valid JSON object with this exact structure:

{{
  "verdict": "OVERCHARGED" or "SLIGHTLY_OVERPRICED" or "FAIR",
  "totalCharged": <number>,
  "totalFair": <number>,
  "totalOvercharge": <number>,
  "summary": "<2 plain-English sentences explaining the verdict>",
  "lineItems": [
    {{
      "name": "<item name>",
      "charged": <number>,
      "fair": <number>,
      "flag": "OVERPRICED" or "UNNECESSARY" or "OK",
      "reason": "<brief explanation of flag>"
    }}
  ],
  "negotiationScript": [
    "<sentence 1 to say to the service advisor>",
    "<sentence 2>",
    "<sentence 3>",
    "<sentence 4>"
  ],
  "questionsToAsk": [
    "<specific question 1>",
    "<specific question 2>",
    "<specific question 3>"
  ]
}}

Return ONLY the JSON object. No explanation, no markdown, no code blocks."""

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = message.content[0].text.strip()
        # Extract JSON if wrapped in anything
        start = text.find('{')
        end = text.rfind('}') + 1
        result = json.loads(text[start:end])
        return jsonify(result)
    except json.JSONDecodeError as e:
        return jsonify({'error': f'Could not parse analysis response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
