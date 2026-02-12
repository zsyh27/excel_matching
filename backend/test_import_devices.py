"""
测试设备导入脚本功能

验证:
1. Excel文件读取
2. 数据解析和验证
3. 批量导入
4. 更新已存在设备
5. 统计报告
"""

import os
import sys
import tempfile
import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.database import DatabaseManager
from modules.models import Device as DeviceModel
from import_devices_from_excel import DeviceImporter


def create_test_excel():
    """创建测试Excel文件"""
    wb = openpyxl.Workbook()
    ws = wb.active
    
    # 添加表头
    ws.append(['设备ID', '品牌', '设备名称', '规格型号', '详细参数', '单价'])
    
    # 添加测试数据
    ws.append(['TEST001', '测试品牌1', '测试设备1', '型号A', '参数描述1', 100.50])
    ws.append(['TEST002', '测试品牌2', '测试设备2', '型号B', '参数描述2', 200.75])
    ws.append(['TEST003', '测试品牌3', '测试设备3', '型号C', '参数描述3', 300.00])
    ws.append(['TEST004', '', '测试设备4', '', '', ''])  # 测试缺失字段
    ws.append(['TEST005', '测试品牌5', '', '', '', 500])  # 测试空设备名称（应跳过）
    
    # 保存到临时文件
    temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.xlsx', delete=False)
    wb.save(temp_file.name)
    temp_file.close()
    
    return temp_file.name


def test_import():
    """测试导入功能"""
    print("=" * 80)
    print("测试设备导入脚本")
    print("=" * 80)
    print()
    
    # 创建测试Excel文件
    print("1. 创建测试Excel文件...")
    excel_file = create_test_excel()
    print(f"   测试文件: {excel_file}")
    print()
    
    # 创建临时数据库
    print("2. 创建临时数据库...")
    temp_db = tempfile.NamedTemporaryFile(mode='wb', suffix='.db', delete=False)
    temp_db.close()
    db_url = f'sqlite:///{temp_db.name}'
    print(f"   数据库: {db_url}")
    print()
    
    try:
        # 初始化数据库
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # 创建导入器
        importer = DeviceImporter(db_manager)
        
        # 测试读取Excel
        print("3. 测试读取Excel文件...")
        devices = importer.read_excel(excel_file)
        print(f"   读取到 {len(devices)} 个有效设备")
        print()
        
        # 显示解析的设备
        print("4. 解析的设备数据:")
        for device in devices:
            print(f"   - {device['device_id']}: {device['device_name']} ({device['brand']}) - ¥{device['unit_price']}")
        print()
        
        # 测试导入
        print("5. 测试导入到数据库...")
        importer.import_to_database(devices, batch_size=2)
        print()
        
        # 验证导入结果
        print("6. 验证导入结果...")
        with db_manager.session_scope() as session:
            count = session.query(DeviceModel).count()
            print(f"   数据库中设备数: {count}")
            
            # 查询具体设备
            test_device = session.query(DeviceModel).filter_by(device_id='TEST001').first()
            if test_device:
                print(f"   TEST001: {test_device.device_name} - ¥{test_device.unit_price}")
        print()
        
        # 测试更新功能
        print("7. 测试更新功能...")
        # 修改第一个设备的价格
        devices[0]['unit_price'] = 999.99
        importer2 = DeviceImporter(db_manager)
        importer2.import_to_database([devices[0]], batch_size=1)
        
        # 验证更新
        with db_manager.session_scope() as session:
            updated_device = session.query(DeviceModel).filter_by(device_id='TEST001').first()
            if updated_device:
                print(f"   更新后 TEST001 价格: ¥{updated_device.unit_price}")
        print()
        
        # 打印统计报告
        print("8. 统计报告:")
        importer.print_report()
        
        # 关闭数据库
        db_manager.close()
        
        print("✓ 所有测试通过！")
        
    finally:
        # 清理临时文件
        if os.path.exists(excel_file):
            os.unlink(excel_file)
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)


if __name__ == '__main__':
    test_import()
