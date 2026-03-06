# 数据库表结构优化方案

## 概述

本文档分析当前数据库表结构与动态表单录入方案的匹配度,并提出优化建议。目标是支持不同设备类型使用不同的特征录入模板,便于后期特征提取和匹配工作。

## 当前表结构分析

### devices表当前字段

```python
class Device(Base):
    __tablename__ = 'devices'
    
    # 基础字段
    device_id = Column(String(100), primary_key=True)
    brand = Column(String(50), nullable=False, index=True)
    device_name = Column(String(100), nullable=False, index=True)
    spec_model = Column(String(200), nullable=False)
    detailed_params = Column(Text, nullable=False)  # ⚠️ 当前必填
    unit_price = Column(Float, nullable=False)
    
    # 智能设备录入新增字段
    raw_description = Column(Text, nullable=True)
    key_params = Column(JSON, nullable=True)  # ⚠️ 结构需要规范化
    confidence_score = Column(Float, nullable=True, index=True)
    
    # ❌ 缺少: device_type字段
```

### 问题识别

1. **缺少device_type字段**: 无法区分设备类型,无法实现动态表单
2. **key_params结构不规范**: 没有明确的JSON结构定义
3. **detailed_params必填**: 与key_params功能重复,应该改为可选
4. **缺少数据来源标识**: 无法区分是手动录入还是智能解析

## 优化方案

### 方案A: 添加device_type字段(推荐)

#### 表结构修改

```python
class Device(Base):
    __tablename__ = 'devices'
    
    # 基础字段
    device_id = Column(String(100), primary_key=True)
    brand = Column(String(50), nullable=False, index=True)
    device_name = Column(String(100), nullable=False, index=True)
    spec_model = Column(String(200), nullable=False)
    
    # ✅ 新增: 设备类型字段
    device_type = Column(String(50), nullable=True, index=True, 
                        comment='设备类型,如:CO2传感器、座阀、温度传感器等')
    
    # ✅ 修改: detailed_params改为可选
    detailed_params = Column(Text, nullable=True, 
                            comment='详细参数文本描述(可选,主要用于向后兼容)')
    
    unit_price = Column(Float, nullable=False)
    
    # 智能设备录入字段
    raw_description = Column(Text, nullable=True, 
                            comment='用户输入的原始设备描述文本')
    
    # ✅ 规范化: key_params结构
    key_params = Column(JSON, nullable=True, 
                       comment='根据设备类型提取的关键参数(JSON格式)')
    
    confidence_score = Column(Float, nullable=True, index=True, 
                             comment='解析结果的置信度评分(0.0-1.0)')
    
    # ✅ 新增: 数据来源标识
    input_method = Column(String(20), nullable=True, default='manual', index=True,
                         comment='录入方式: manual(手动), intelligent(智能解析), excel(Excel导入)')
    
    # ✅ 新增: 创建和更新时间
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联规则 - 级联删除
    rules = relationship("Rule", back_populates="device", cascade="all, delete-orphan")
```

#### key_params JSON结构规范

```json
{
  "量程": {
    "value": "0-2000 ppm",
    "raw_value": "0-2000 ppm",
    "data_type": "range",
    "unit": "ppm",
    "confidence": 0.95
  },
  "输出信号": {
    "value": "4-20 mA",
    "raw_value": "4-20mA",
    "data_type": "string",
    "unit": "mA",
    "confidence": 0.98
  },
  "精度": {
    "value": "±50 ppm",
    "raw_value": "±50ppm",
    "data_type": "string",
    "unit": null,
    "confidence": 0.90
  }
}
```

**字段说明**:
- `value`: 标准化后的参数值
- `raw_value`: 原始提取的参数值
- `data_type`: 数据类型(range/number/string)
- `unit`: 单位
- `confidence`: 该参数提取的置信度(0.0-1.0)

### 方案B: 保持现有结构,仅添加device_type(备选)

如果不想大幅修改现有结构,可以仅添加device_type字段:

```python
# 仅添加
device_type = Column(String(50), nullable=True, index=True)
```

其他字段保持不变,但这样会有以下限制:
- detailed_params仍然必填,与key_params功能重复
- 无法区分数据来源
- 缺少时间戳字段

## 推荐方案: 方案A

### 优势

1. **支持动态表单**: device_type字段可以用于选择不同的录入模板
2. **数据结构清晰**: key_params规范化后便于特征提取
3. **向后兼容**: detailed_params改为可选,旧数据仍然有效
4. **可追溯性**: input_method和时间戳字段便于数据管理
5. **便于匹配**: 规范化的key_params便于特征提取和权重分配

### 实施步骤

#### 1. 数据库迁移脚本

```python
# backend/migrations/add_device_type_and_optimize_schema.py

from sqlalchemy import text
from backend.modules.database_manager import DatabaseManager
import json

def migrate():
    """添加device_type字段并优化表结构"""
    
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    
    with db_manager.session_scope() as session:
        # 1. 添加新字段
        session.execute(text("""
            ALTER TABLE devices 
            ADD COLUMN device_type VARCHAR(50);
        """))
        
        session.execute(text("""
            ALTER TABLE devices 
            ADD COLUMN input_method VARCHAR(20) DEFAULT 'manual';
        """))
        
        session.execute(text("""
            ALTER TABLE devices 
            ADD COLUMN created_at DATETIME;
        """))
        
        session.execute(text("""
            ALTER TABLE devices 
            ADD COLUMN updated_at DATETIME;
        """))
        
        # 2. 修改detailed_params为可选(SQLite不支持直接修改,需要重建表)
        # 注意: SQLite需要使用重建表的方式
        
        # 3. 为现有数据设置默认值
        session.execute(text("""
            UPDATE devices 
            SET input_method = 'manual',
                created_at = datetime('now'),
                updated_at = datetime('now')
            WHERE input_method IS NULL;
        """))
        
        # 4. 创建索引
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_device_type 
            ON devices(device_type);
        """))
        
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_input_method 
            ON devices(input_method);
        """))
        
        print("✅ 数据库迁移完成")
        print("  - 添加device_type字段")
        print("  - 添加input_method字段")
        print("  - 添加created_at和updated_at字段")
        print("  - 创建相关索引")

if __name__ == "__main__":
    migrate()
```

#### 2. 更新ORM模型

修改`backend/modules/models.py`:

```python
from datetime import datetime

class Device(Base):
    __tablename__ = 'devices'
    
    device_id = Column(String(100), primary_key=True)
    brand = Column(String(50), nullable=False, index=True)
    device_name = Column(String(100), nullable=False, index=True)
    spec_model = Column(String(200), nullable=False)
    device_type = Column(String(50), nullable=True, index=True)
    detailed_params = Column(Text, nullable=True)  # 改为可选
    unit_price = Column(Float, nullable=False)
    
    raw_description = Column(Text, nullable=True)
    key_params = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True, index=True)
    input_method = Column(String(20), nullable=True, default='manual', index=True)
    
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    rules = relationship("Rule", back_populates="device", cascade="all, delete-orphan")
```

#### 3. 更新数据类

修改`backend/modules/data_classes.py`:

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class Device:
    device_id: str
    brand: str
    device_name: str
    spec_model: str
    unit_price: float
    
    device_type: Optional[str] = None
    detailed_params: Optional[str] = None
    raw_description: Optional[str] = None
    key_params: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    input_method: str = 'manual'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

#### 4. 更新DatabaseLoader转换方法

```python
def _model_to_device(self, device_model: DeviceModel) -> Device:
    """将ORM模型转换为数据类"""
    return Device(
        device_id=device_model.device_id,
        brand=device_model.brand,
        device_name=device_model.device_name,
        spec_model=device_model.spec_model,
        unit_price=device_model.unit_price,
        device_type=device_model.device_type,
        detailed_params=device_model.detailed_params,
        raw_description=device_model.raw_description,
        key_params=device_model.key_params,
        confidence_score=device_model.confidence_score,
        input_method=device_model.input_method,
        created_at=device_model.created_at,
        updated_at=device_model.updated_at
    )

def _device_to_model(self, device: Device) -> DeviceModel:
    """将数据类转换为ORM模型"""
    return DeviceModel(
        device_id=device.device_id,
        brand=device.brand,
        device_name=device.device_name,
        spec_model=device.spec_model,
        unit_price=device.unit_price,
        device_type=device.device_type,
        detailed_params=device.detailed_params,
        raw_description=device.raw_description,
        key_params=device.key_params,
        confidence_score=device.confidence_score,
        input_method=device.input_method or 'manual',
        created_at=device.created_at,
        updated_at=device.updated_at
    )
```

## 动态表单实现方案

### 前端表单设计

```vue
<template>
  <el-form :model="deviceForm" :rules="formRules" ref="deviceFormRef">
    <!-- 基础信息 -->
    <el-form-item label="设备ID" prop="device_id">
      <el-input v-model="deviceForm.device_id" />
    </el-form-item>
    
    <el-form-item label="品牌" prop="brand">
      <el-select v-model="deviceForm.brand" filterable>
        <el-option v-for="brand in brands" :key="brand" :value="brand" />
      </el-select>
    </el-form-item>
    
    <!-- ✅ 设备类型选择 - 触发动态表单 -->
    <el-form-item label="设备类型" prop="device_type">
      <el-select 
        v-model="deviceForm.device_type" 
        @change="onDeviceTypeChange"
        filterable
      >
        <el-option 
          v-for="type in deviceTypes" 
          :key="type" 
          :value="type" 
        />
      </el-select>
    </el-form-item>
    
    <el-form-item label="设备名称" prop="device_name">
      <el-input v-model="deviceForm.device_name" />
    </el-form-item>
    
    <el-form-item label="规格型号" prop="spec_model">
      <el-input v-model="deviceForm.spec_model" />
    </el-form-item>
    
    <!-- ✅ 动态参数表单 - 根据device_type显示 -->
    <div v-if="deviceForm.device_type" class="dynamic-params">
      <h4>设备参数</h4>
      <el-form-item 
        v-for="param in currentDeviceParams" 
        :key="param.name"
        :label="param.name"
        :prop="`key_params.${param.name}`"
        :required="param.required"
      >
        <el-input 
          v-model="deviceForm.key_params[param.name]"
          :placeholder="`请输入${param.name},单位:${param.unit || '无'}`"
        />
        <span class="param-hint">{{ param.hint }}</span>
      </el-form-item>
    </div>
    
    <!-- 详细参数(可选) -->
    <el-form-item label="详细参数(可选)" prop="detailed_params">
      <el-input 
        v-model="deviceForm.detailed_params" 
        type="textarea"
        :rows="3"
        placeholder="可选填写,如有特殊参数可在此补充"
      />
    </el-form-item>
    
    <el-form-item label="单价" prop="unit_price">
      <el-input-number v-model="deviceForm.unit_price" :min="0" :precision="2" />
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, computed } from 'vue'
import deviceParamsConfig from '@/config/device_params.json'

const deviceForm = ref({
  device_id: '',
  brand: '',
  device_type: '',
  device_name: '',
  spec_model: '',
  key_params: {},
  detailed_params: '',
  unit_price: 0,
  input_method: 'manual'
})

// 设备类型列表
const deviceTypes = computed(() => {
  return Object.keys(deviceParamsConfig.device_types)
})

// 当前设备类型的参数配置
const currentDeviceParams = computed(() => {
  if (!deviceForm.value.device_type) return []
  return deviceParamsConfig.device_types[deviceForm.value.device_type]?.params || []
})

// 设备类型变更时
const onDeviceTypeChange = (newType) => {
  // 清空之前的参数
  deviceForm.value.key_params = {}
  
  // 初始化新类型的参数
  const params = deviceParamsConfig.device_types[newType]?.params || []
  params.forEach(param => {
    deviceForm.value.key_params[param.name] = ''
  })
}
</script>
```

### 后端API支持

```python
# backend/app.py

@app.route('/api/device-types', methods=['GET'])
def get_device_types():
    """获取所有设备类型及其参数配置"""
    try:
        import yaml
        with open('backend/config/device_params.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return jsonify({
            'success': True,
            'data': {
                'device_types': list(config['device_types'].keys()),
                'params_config': config['device_types']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error_message': str(e)
        }), 500

@app.route('/api/devices', methods=['POST'])
def create_device():
    """创建设备 - 支持动态参数"""
    try:
        data = request.json
        
        # 验证必填字段
        required_fields = ['device_id', 'brand', 'device_name', 'spec_model', 'unit_price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error_message': f'缺少必填字段: {field}'
                }), 400
        
        # 创建设备对象
        device = Device(
            device_id=data['device_id'],
            brand=data['brand'],
            device_name=data['device_name'],
            spec_model=data['spec_model'],
            unit_price=data['unit_price'],
            device_type=data.get('device_type'),
            key_params=data.get('key_params'),
            detailed_params=data.get('detailed_params'),
            input_method=data.get('input_method', 'manual')
        )
        
        # 保存到数据库
        success = db_loader.add_device(device, auto_generate_rule=data.get('auto_generate_rule', True))
        
        if success:
            return jsonify({
                'success': True,
                'data': {'device_id': device.device_id},
                'message': '设备创建成功'
            })
        else:
            return jsonify({
                'success': False,
                'error_message': '设备创建失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error_message': str(e)
        }), 500
```

## 特征提取优化

### 基于device_type的特征提取

```python
# backend/modules/rule_generator.py

class RuleGenerator:
    def extract_features(self, device: Device) -> List[str]:
        """提取设备特征 - 优化版"""
        features = []
        
        # 1. 品牌特征(高权重)
        if device.brand:
            features.append(device.brand)
        
        # 2. 设备类型特征(高权重)
        if device.device_type:
            features.append(device.device_type)
        
        # 3. 型号特征(高权重)
        if device.spec_model:
            features.append(device.spec_model)
        
        # 4. 关键参数特征(中权重) - 从key_params提取
        if device.key_params:
            for param_name, param_data in device.key_params.items():
                if isinstance(param_data, dict):
                    value = param_data.get('value', '')
                else:
                    value = str(param_data)
                
                if value:
                    # 提取参数值中的关键词
                    tokens = self.preprocessor.preprocess(value)
                    features.extend(tokens)
        
        # 5. 设备名称特征(中权重)
        if device.device_name:
            tokens = self.preprocessor.preprocess(device.device_name)
            features.extend(tokens)
        
        # 6. 详细参数特征(低权重) - 仅当key_params为空时使用
        if not device.key_params and device.detailed_params:
            tokens = self.preprocessor.preprocess(device.detailed_params)
            features.extend(tokens)
        
        # 去重
        return list(set(features))
    
    def assign_weights(self, features: List[str], device: Device) -> Dict[str, float]:
        """分配特征权重 - 优化版"""
        weights = {}
        
        for feature in features:
            # 品牌权重: 3.0
            if device.brand and feature == device.brand:
                weights[feature] = 3.0
            
            # 设备类型权重: 3.0
            elif device.device_type and feature == device.device_type:
                weights[feature] = 3.0
            
            # 型号权重: 3.0
            elif device.spec_model and feature in device.spec_model:
                weights[feature] = 3.0
            
            # 关键参数权重: 2.5
            elif device.key_params and any(
                feature in str(param_data.get('value', '')) 
                for param_data in device.key_params.values()
                if isinstance(param_data, dict)
            ):
                weights[feature] = 2.5
            
            # 设备名称关键词权重: 2.0
            elif device.device_name and feature in device.device_name:
                weights[feature] = 2.0
            
            # 其他特征权重: 1.0
            else:
                weights[feature] = 1.0
        
        return weights
```

## 数据迁移策略

### 旧数据兼容性

1. **device_type为空的旧数据**: 
   - 保持device_type为NULL
   - 使用detailed_params进行特征提取
   - 前端显示时使用统一表单

2. **新数据**:
   - 必须填写device_type
   - 使用动态表单录入key_params
   - detailed_params可选

### 迁移脚本

```python
# backend/scripts/migrate_old_devices.py

def migrate_old_devices():
    """为旧设备数据推断device_type"""
    
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    
    with db_manager.session_scope() as session:
        # 查询所有device_type为空的设备
        old_devices = session.query(DeviceModel).filter(
            DeviceModel.device_type == None
        ).all()
        
        print(f"找到 {len(old_devices)} 个需要迁移的设备")
        
        for device in old_devices:
            # 根据device_name推断device_type
            device_type = infer_device_type(device.device_name)
            
            if device_type:
                device.device_type = device_type
                device.input_method = 'manual'
                device.updated_at = datetime.utcnow()
                print(f"  - {device.device_id}: {device.device_name} -> {device_type}")
        
        session.commit()
        print(f"✅ 迁移完成")

def infer_device_type(device_name: str) -> Optional[str]:
    """根据设备名称推断设备类型"""
    device_types = {
        'CO2传感器': ['CO2', '二氧化碳'],
        '温度传感器': ['温度', '温感', 'temperature'],
        '压力传感器': ['压力', '压感', 'pressure'],
        '座阀': ['座阀', '调节阀'],
        '执行器': ['执行器', 'actuator'],
        # ... 更多类型
    }
    
    for device_type, keywords in device_types.items():
        if any(keyword in device_name for keyword in keywords):
            return device_type
    
    return None
```

## 总结

### 推荐实施方案A的理由

1. **完全支持动态表单**: device_type字段是核心
2. **数据结构清晰**: key_params规范化便于特征提取
3. **向后兼容**: 旧数据仍然可用
4. **便于维护**: 数据来源和时间戳便于追溯
5. **提升匹配准确度**: 规范化的参数便于权重分配

### 工作量评估

- 数据库迁移脚本: 0.5天
- ORM模型更新: 0.5天
- DatabaseLoader更新: 1天
- 前端动态表单: 2天
- 后端API支持: 1天
- 特征提取优化: 1天
- 测试和调试: 1天

**总计**: 约7天

### 风险评估

- **低风险**: 向后兼容,旧数据不受影响
- **中等复杂度**: 需要更新多个模块
- **高收益**: 显著提升录入效率和匹配准确度
