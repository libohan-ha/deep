from flask import Flask, render_template, request, jsonify, Response
import requests
import json
import os

app = Flask(__name__)

# Dify API配置
API_KEY = "app-ObC7pyZXezrRUAU60kC29W4h"
API_URL = "https://api.dify.ai/v1/chat-messages"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/research', methods=['POST'])
def research():
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({"error": "请输入研究概念"}), 400
    
    # 构建请求Dify API的数据
    dify_data = {
        "inputs": {},
        "query": query,
        "response_mode": "streaming",
        "conversation_id": "",
        "user": "user-" + os.urandom(4).hex(),
        "files": []
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 使用流式响应
    def generate():
        response = requests.post(
            API_URL,
            headers=headers,
            json=dify_data,
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data:'):
                    try:
                        data_json = json.loads(line_text[5:])
                        if 'event' in data_json and data_json['event'] == 'message':
                            yield f"data: {json.dumps(data_json)}\n\n"
                    except json.JSONDecodeError:
                        continue
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    # 确保templates目录存在
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True, port=5002)