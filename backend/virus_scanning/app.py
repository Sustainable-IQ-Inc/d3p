from flask import Flask, request, jsonify
import os
import subprocess

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def scan_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    file_path = f'/tmp/{file.filename}'
    file.save(file_path)

    result = subprocess.run(['/usr/local/bin/scan.sh', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #add logging with the result of the scan
    print(result.stdout.decode('utf-8'))
    print(result.stderr.decode('utf-8'))
    os.remove(file_path)
    return jsonify({"output": result.stdout.decode('utf-8')}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
