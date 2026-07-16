from flask import Flask, request, jsonify
from flask_cors import CORS
from curl_cffi import requests as cffi_requests

app = Flask(__name__)
CORS(app)

session = cffi_requests.Session(impersonate='chrome120')

FIELDS = ','.join([
    'regularMarketPrice','regularMarketPreviousClose',
    'preMarketPrice','preMarketChange','preMarketChangePercent',
    'postMarketPrice','postMarketChange','postMarketChangePercent',
    'overnightMarketPrice','overnightMarketChange','overnightMarketChangePercent','overnightMarketTime',
    'marketState'
])

@app.route('/quote')
def quote():
    tickers = [t.strip().upper() for t in request.args.get('tickers', '').split(',') if t.strip()]
    crumb = request.args.get('crumb', '')
    symbols = ','.join(tickers)

    if not crumb:
        return jsonify({'error': 'crumb required'}), 400

    try:
        url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols}&fields={FIELDS}&crumb={crumb}&formatted=false&region=US&lang=en-US'
        r = session.get(url, timeout=10)
        data = r.json()
        quotes = data.get('quoteResponse', {}).get('result', [])
        result = {}
        for q in quotes:
            ticker = q.get('symbol')
            result[ticker] = {
                'marketState':              q.get('marketState'),
                'regularMarketPrice':       q.get('regularMarketPrice'),
                'previousClose':            q.get('regularMarketPreviousClose'),
                'preMarketPrice':           q.get('preMarketPrice'),
                'preMarketChange':          q.get('preMarketChange'),
                'preMarketChangePct':       q.get('preMarketChangePercent'),
                'postMarketPrice':          q.get('postMarketPrice'),
                'postMarketChange':         q.get('postMarketChange'),
                'postMarketChangePct':      q.get('postMarketChangePercent'),
                'overnightMarketPrice':     q.get('overnightMarketPrice'),
                'overnightMarketChange':    q.get('overnightMarketChange'),
                'overnightMarketChangePct': q.get('overnightMarketChangePercent'),
                'overnightMarketTime':      q.get('overnightMarketTime'),
            }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
