#!/usr/bin/env python
import json, time
try:
    import requests
except Exception:
    requests = None
from urllib import request as urlreq

CASES_PATH = 'bench/cases.json'
RESULTS_PATH = 'bench/results.json'
URL = 'http://127.0.0.1:5000/api/analyze'

# Read cases robustly (handle BOM)
with open(CASES_PATH, 'rb') as f:
    raw = f.read()
try:
    text = raw.decode('utf-8-sig')
except Exception:
    text = raw.decode('utf-8', errors='ignore')
cases = json.loads(text)

results = []
for c in cases:
    payload = {'prompt': c['prompt']}
    start = time.time()
    try:
        if requests:
            r = requests.post(URL, json=payload, timeout=10)
            text = r.text
            status_code = r.status_code
        else:
            data = json.dumps(payload).encode('utf8')
            req = urlreq.Request(URL, data=data, headers={'Content-Type':'application/json'})
            with urlreq.urlopen(req, timeout=10) as resp:
                text = resp.read().decode('utf8')
            status_code = 200
        duration = time.time() - start
        try:
            response_payload = json.loads(text)
        except json.JSONDecodeError:
            response_payload = {}
        score = response_payload.get('risk_scoring_engine', {}).get('calculated_score')
        classification = response_payload.get('risk_classification')
        results.append({
            'id': c['id'],
            'attack_type': c['attack_type'],
            'status_code': status_code,
            'risk_score': score,
            'risk_classification': classification,
            'response': text[:200],
            'duration': duration
        })
        print(f"[OK] {c['id']} {c['attack_type']} ({duration:.2f}s)")
    except Exception as e:
        duration = time.time() - start
        results.append({
            'id': c['id'],
            'attack_type': c['attack_type'],
            'status_code': None,
            'error': str(e),
            'duration': duration
        })
        print(f"[ERR] {c['id']} {c['attack_type']} -> {e}")

with open(RESULTS_PATH, 'w', encoding='utf8') as f:
    json.dump(results, f, indent=2)

# Simple summary
ok = sum(1 for r in results if r.get('status_code')==200)
err = len(results) - ok
print('\nBenchmark completed.\nTotal cases:', len(results), 'OK:', ok, 'Errors:', err)
benign = [r for r in results if r['attack_type'].startswith('benign')]
threats = [r for r in results if not r['attack_type'].startswith('benign')]
benign_clean = sum(1 for r in benign if (r.get('risk_score') or 0) == 0)
threats_flagged = sum(1 for r in threats if (r.get('risk_score') or 0) > 0)
print('Benign cases:', len(benign), 'clean:', benign_clean)
print('Threat cases:', len(threats), 'flagged:', threats_flagged)
