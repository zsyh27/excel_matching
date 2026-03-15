import urllib.request
import json

BASE = 'http://localhost:5000'

def get(path):
    try:
        with urllib.request.urlopen(BASE + path) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'error': str(e)}

print('=== /api/statistics/match-success-rate ===')
data = get('/api/statistics/match-success-rate')
print(json.dumps(data, ensure_ascii=False, indent=2))
