import json
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

URL = 'http://localhost:8002/pedidos/'
NUM = 50

def task(i):
    data = json.dumps({'itens': [1]}).encode('utf-8')
    req = Request(URL, data=data, headers={'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urlopen(req, timeout=30) as resp:
            status = resp.getcode()
            body = resp.read().decode('utf-8')
            return (i, status, time.time() - t0)
    except HTTPError as e:
        return (i, e.code, time.time() - t0)
    except URLError as e:
        return (i, 'EXC', time.time() - t0)

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=NUM) as ex:
        futures = [ex.submit(task, i) for i in range(NUM)]
        results = [f.result() for f in futures]

    codes = [r[1] for r in results]
    times = [r[2] for r in results]

    from collections import Counter
    print('counts', Counter(codes))
    print('latency_mean', statistics.mean(times))
    print('latency_p95', sorted(times)[int(0.95 * len(times)) - 1])
    print('samples', results[:10])
