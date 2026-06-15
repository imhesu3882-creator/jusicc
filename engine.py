import time
import json
from datetime import datetime

while True:
    data = {
        "time": str(datetime.now()),
        "cash": 10000000,
        "note": "engine running"
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("running engine...")
    time.sleep(10)
