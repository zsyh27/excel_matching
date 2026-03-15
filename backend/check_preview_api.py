#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查预览 API 响应结构"""

import requests
import json

BASE_URL = 'http://localhost:5000'
test_text = "CO浓度探测器 量程0~250ppm"

response = requests.post(
    f"{BASE_URL}/api/intelligent-extraction/preview",
    json={"text": test_text},
    timeout=10
)

print("响应状态码:", response.status_code)
print("\n响应内容:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
