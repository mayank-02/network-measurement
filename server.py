from flask import Flask, send_file

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return "200 OK", 200

@app.route('/large-content', methods=['GET'])
def serve_html():
    return send_file('index.html', mimetype='text/html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
