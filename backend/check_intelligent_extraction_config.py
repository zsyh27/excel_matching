#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查 intelligent_extraction 配置结构"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

config = db_loader.get_config_by_key('intelligent_extraction')

if config:
    print("intelligent_extraction 配置结构:")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print()
    print(f"顶层键: {list(config.keys())}")
else:
    print("intelligent_extraction 配置不存在")
