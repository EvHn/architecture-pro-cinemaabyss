import os
import random
import requests
from flask import Flask, request

app = Flask(__name__)

# Конфигурация из переменных окружения
PORT = os.environ['PORT']
MONOLITH_URL = os.environ['MONOLITH_URL']
MOVIES_SERVICE_URL = os.environ['MOVIES_SERVICE_URL']
MOVIES_MIGRATION_PERCENT = int(os.environ.get('MOVIES_MIGRATION_PERCENT', 0))
GRADUAL_MIGRATION = os.environ.get('GRADUAL_MIGRATION', 'false').lower() == 'true'


@app.route('/api/proxy/health', methods=['GET'])
def healthcheck():
    return {"status": True}


@app.route('/<path>', methods=['GET', 'POST'])
@app.route('/api/<path>', methods=['GET', 'POST'])
def proxy(path):
    # Определение целевого сервиса
    if path.startswith('movies'):
        if GRADUAL_MIGRATION and random.randint(1, 100) <= MOVIES_MIGRATION_PERCENT:
            target_url = MOVIES_SERVICE_URL
        else:
            target_url = MONOLITH_URL
    else:
        target_url = MONOLITH_URL

    # Формируем полный URL
    if not path.endswith('health'):
        path = f'api/{path}'
    url = f"{target_url.rstrip('/')}/{path}"
    print(f"target_url: {url}")

    # Проксирование запроса
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={k: v for k, v in request.headers if k.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            params=request.args
        )
    except requests.exceptions.RequestException as e:
        return str(e), 502

    return resp.content


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
