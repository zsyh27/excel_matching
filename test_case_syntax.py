import sqlite3, sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, func, case as sa_case
from sqlalchemy.orm import sessionmaker
from modules.models import MatchLog

engine = create_engine('sqlite:///data/devices.db')
Session = sessionmaker(bind=engine)
session = Session()

try:
    result = session.query(
        func.strftime('%Y-%m-%d', MatchLog.timestamp).label('date'),
        func.count(MatchLog.log_id).label('total'),
        func.sum(sa_case((MatchLog.match_status == 'success', 1), else_=0)).label('success')
    ).group_by(
        func.strftime('%Y-%m-%d', MatchLog.timestamp)
    ).all()
    
    print('查询成功!')
    for row in result:
        print(f'  日期={row.date}, 总数={row.total}, 成功={row.success}')
except Exception as e:
    print(f'查询失败: {e}')
    import traceback
    traceback.print_exc()
finally:
    session.close()
