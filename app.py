import os, json, anthropic
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
    prompt = f"""You are Consumer Defender Car Repair Defense AI. Analyze this repair estimate and return ONLY valid JSON.\n\n{vehicle_info}\n\nESTIMATE:\n{estimate_text}\n\nReturn this exact JSON:\n{{"verdict":"OVERCHARGED or SLIGHTLY_OVERPRICED or FAIR","totalCharged":0,"totalFair":0,"totalOvercharge":0,"summary":"2 sentences","lineItems":[{{"name":"string","charged":0,"fair":0,"flag":"OVERPRICED or UNNECESSARY or OK","reason":"brief"}}],"negotiationScript":["line1","line2","line3","line4"],"questionsToAsk":["q1","q2","q3"]}}\n\nOnly return JSON, nothing else."""
    try:
        message = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1500, messages=[{"role":"user","content":prompt}])
        text = message.content[0].text
        result = json.loads(text[text.find('{'):text.rfind('}')+1])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
