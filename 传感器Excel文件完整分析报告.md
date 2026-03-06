# 传感器Excel文件完整分析报告（5组数据）

## 📊 一、数据概览

### 基本信息
- **文件名**: 室内温湿度传感器价格表.xlsx
- **总行数**: 151行
- **总列数**: 8列
- **设备总数**: 137条
- **分组数量**: 5个

### 数据分布

| 分组 | 设备类型 | 数量 | 数据质量 | 处理难度 |
|------|---------|------|---------|---------|
| 1 | 室内温度/温湿度传感器 | 21条 | ✅ 优秀 | 低 |
| 2 | 风管温度/温湿度传感器 | 21条 | ✅ 优秀 | 低 |
| 3 | 室外温度/温湿度传感器 | 2条 | ✅ 优秀 | 低 |
| 4 | 电流/电压输出型传感器 | 58条 | ✅ 良好 | 低 |
| 5 | 现场设备（多功能传感器） | 35条 | ⚠️ 需处理 | 中 |

---

## 📋 二、各分组详细分析

### 分组1：室内温度/温湿度传感器（21条）

#### 字段结构
```
型号 | 价格 | 安装位置 | 湿度信号 | 湿度精度 | 温度信号
```

#### 设备类型识别
- **温度传感器**：型号以 `HST-R` 开头（3条）
  - 湿度信号为"无"
  - 只有温度信号
  
- **温湿度传感器**：型号以 `HSH-R` 开头（18条）
  - 湿度信号：4-20mA 或 0-10V
  - 湿度精度：±2%、±3%、±5%
  - 温度信号：NTC 10K、NTC 20K、Pt1000

#### 数据示例
```
HST-RA    | 213.22 | 室内墙装 | 无      | -    | NTC 10K
HSH-RM2A  | 623.99 | 室内墙装 | 4-20mA  | 0.02 | NTC 10K
```

#### 录入建议
- **设备类型**: 温度传感器 / 温湿度传感器
- **检测对象**: 温度 / 温度+湿度
- **安装位置**: 室内墙装
- **key_params**:
  ```json
  {
    "检测对象": {"value": "温度+湿度"},
    "安装位置": {"value": "室内墙装"},
    "温度信号类型": {"value": "NTC 10K"},
    "湿度信号类型": {"value": "4-20mA"},
    "湿度精度": {"value": "±2%", "unit": "%"}
  }
  ```

---

### 分组2：风管温度/温湿度传感器（21条）

#### 字段结构
```
型号 | 价格 | 安装位置 | 湿度信号 | 湿度精度 | 温度信号
```

#### 设备类型识别
- **温度传感器**：型号以 `HST-D` 开头（3条）
- **温湿度传感器**：型号以 `HSH-D` 开头（18条）

#### 数据示例
```
HST-DA    | 186.22 | 风管 | 无      | -    | NTC 10K
HSH-DM2A  | 658.11 | 风管 | 4-20mA  | 0.02 | NTC 10K
```

#### 录入建议
- **设备类型**: 温度传感器 / 温湿度传感器
- **检测对象**: 温度 / 温度+湿度
- **安装位置**: 风管
- 其他参数同分组1

---

### 分组3：室外温度/温湿度传感器（2条）

#### 字段结构
```
型号 | 价格 | 安装位置 | 湿度信号 | 湿度精度 | 温度信号
```

#### 设备类型识别
- **温湿度传感器**：型号以 `HSH-E` 开头（2条）

#### 数据示例
```
HSH-EM3B  | 658.11 | 室外 | 4-20mA  | 0.03 | NTC 20K
HSH-EV3B  | 658.11 | 室外 | 0-10V   | 0.03 | NTC 20K
```

#### 录入建议
- **设备类型**: 温湿度传感器
- **检测对象**: 温度+湿度
- **安装位置**: 室外
- 其他参数同分组1

---

### 分组4：电流/电压输出型传感器（58条）

#### 字段结构
```
型号 | 价格 | 产品类型 | 输出信号 | 温度传感器元器件类型 | 湿度精度
```

#### 设备类型识别
根据"产品类型"字段：
- **风管温湿度传感器**（约30条）
- **室内温湿度传感器**（约20条）
- **室内温度传感器**（约8条）

#### 数据示例
```
HSH-DM2M-P | 775.63 | 风管温湿度传感器 | 4-20mA | Pt1000 | ±2%
HST-RV-E   | 314.25 | 室内温度传感器   | 0-10V  | 电子式 | N/A
```

#### 录入建议
- **设备类型**: 直接使用"产品类型"字段
- **检测对象**: 根据产品类型判断
- **key_params**:
  ```json
  {
    "检测对象": {"value": "温度+湿度"},
    "输出信号": {"value": "4-20mA"},
    "温度传感器类型": {"value": "Pt1000"},
    "湿度精度": {"value": "±2%", "unit": "%"}
  }
  ```

---

### 分组5：现场设备（35条）⚠️ 重点关注

#### 字段结构
```
型号 | 价格 | 说明 | 备注
```

#### 设备类型分布

| 设备类型 | 数量 | 特点 |
|---------|------|------|
| **空气质量传感器** | 4条 | 多功能集成，带显示屏 |
| **CO2传感器** | 18条 | 包含多功能组合型 |
| **CO传感器** | 12条 | 单一功能 |
| **其他** | 1条 | 一氧化碳传感器 |

#### 数据示例

**示例1：空气质量传感器**
```
型号: HAQ61L
价格: 2567.16
说明: 室内空气质量传感器，带显示屏，显示状态长暗，面板黑色
备注: (空)
```

**示例2：多功能CO2传感器**
```
型号: HAQ41L
价格: 1299.50
说明: 温度，湿度，二氧化碳，PM2.5
备注: 24VDC，有显示屏，靠近点亮，黑色
```

**示例3：CO传感器**
```
型号: HSCM-R100U
价格: 1085.365
说明: CO传感器 0-100PPM,4-20mA/0-10V/2-10V信号,无显示，无继电器输出
备注: (空)
```

**示例4：CO2传感器**
```
型号: HSCD-R1UL
价格: 995.982
说明: 室内单通道CO2,带显示，4-20mA/0-10V/2-10V信号
备注: (空)
```

#### 数据特点分析

##### ✅ 优点
1. 包含了CO、CO2、PM2.5等多种传感器类型
2. 说明字段信息丰富

##### ⚠️ 挑战
1. **说明字段混合多种信息**：
   - 设备类型
   - 检测对象（可能是多个）
   - 量程
   - 输出信号
   - 显示屏信息
   - 外观信息（颜色）
   - 其他功能（继电器等）

2. **信息格式不统一**：
   - 有的用逗号分隔
   - 有的用中文顿号分隔
   - 有的混合中英文

3. **需要智能解析**：
   - 识别设备类型
   - 提取检测对象
   - 解析量程信息
   - 提取输出信号

#### 录入策略

##### 策略A：智能解析（推荐）

创建解析规则：

```python
def parse_group5_device(row):
    """解析第5组设备信息"""
    model = row[0]
    price = row[1]
    description = row[2]
    remark = row[3] if len(row) > 3 else ""
    
    # 1. 识别设备类型
    if '空气质量' in description:
        device_type = '空气质量传感器'
        detection_objects = extract_air_quality_params(description)
    elif 'CO2' in description or '二氧化碳' in description:
        device_type = 'CO2传感器'
        detection_objects = extract_co2_params(description)
    elif 'CO' in description and 'CO2' not in description:
        device_type = 'CO传感器'
        detection_objects = extract_co_params(description)
    elif 'PM' in description:
        device_type = 'PM传感器'
        detection_objects = extract_pm_params(description)
    
    # 2. 提取检测对象
    # 从"温度，湿度，二氧化碳，PM2.5"这样的格式中提取
    
    # 3. 提取量程
    # 从"0-100PPM"、"0-2000ppm"这样的格式中提取
    
    # 4. 提取输出信号
    # 从"4-20mA/0-10V/2-10V"这样的格式中提取
    
    # 5. 提取其他特征
    # 显示屏、颜色、继电器等
    
    return standardized_device
```

##### 策略B：手动分类（备选）

将35条数据按设备类型分类后，手动整理成标准格式。

---

## 🎯 三、统一录入方案

### 方案概述

采用**分组处理 + 智能解析**的策略：

1. **前4组（102条）**：结构清晰，直接转换
2. **第5组（35条）**：需要智能解析

### 标准化字段映射

#### 必填字段
| 系统字段 | 来源 | 说明 |
|---------|------|------|
| brand | 手动补充 | 需要确认品牌 |
| device_type | 解析得出 | 温度传感器/温湿度传感器/CO2传感器/CO传感器/PM传感器/空气质量传感器 |
| device_name | 组合生成 | 如"室内温湿度传感器" |
| spec_model | 型号列 | 直接使用 |
| unit_price | 价格列 | 直接使用 |

#### key_params字段

**温度/温湿度传感器（前4组）**:
```json
{
  "检测对象": {"value": "温度+湿度", "required": true},
  "安装位置": {"value": "室内墙装", "required": false},
  "温度信号类型": {"value": "NTC 10K", "required": false},
  "湿度信号类型": {"value": "4-20mA", "required": false},
  "湿度精度": {"value": "±2%", "unit": "%", "required": false},
  "输出信号": {"value": "4-20mA", "required": false}
}
```

**CO2传感器（第5组）**:
```json
{
  "检测对象": {"value": "CO2", "required": true},
  "量程": {"value": "0-2000", "unit": "ppm", "required": true},
  "输出信号": {"value": "4-20mA/0-10V", "required": true},
  "显示屏": {"value": "带显示", "required": false},
  "通道数": {"value": "单通道", "required": false}
}
```

**CO传感器（第5组）**:
```json
{
  "检测对象": {"value": "CO", "required": true},
  "量程": {"value": "0-100", "unit": "ppm", "required": true},
  "输出信号": {"value": "4-20mA/0-10V", "required": true},
  "显示屏": {"value": "无显示", "required": false},
  "继电器": {"value": "无继电器", "required": false}
}
```

**空气质量传感器（第5组）**:
```json
{
  "检测对象": {"value": "CO2+PM2.5+温度+湿度", "required": true},
  "显示屏": {"value": "带显示屏", "required": false},
  "显示状态": {"value": "长暗", "required": false},
  "面板颜色": {"value": "黑色", "required": false},
  "电源": {"value": "24VDC", "required": false}
}
```

---

## 🔧 四、数据清洗脚本设计

### 脚本功能模块

```python
# 模块1：读取Excel
def load_excel_data(file_path):
    """加载Excel文件，识别5个分组"""
    pass

# 模块2：处理前4组（简单转换）
def process_groups_1_to_4(sections):
    """处理结构清晰的前4组数据"""
    for section in sections[:4]:
        for row in section['data']:
            device = {
                'brand': '霍尼韦尔',  # 需要确认
                'device_type': identify_device_type(row, section),
                'device_name': generate_device_name(row, section),
                'spec_model': row[0],
                'unit_price': row[1],
                'key_params': extract_key_params_simple(row, section)
            }
            yield device

# 模块3：处理第5组（智能解析）
def process_group_5(section):
    """处理第5组现场设备数据"""
    for row in section['data']:
        # 解析说明字段
        parsed_info = parse_description(row[2], row[3])
        
        device = {
            'brand': '霍尼韦尔',  # 需要确认
            'device_type': parsed_info['device_type'],
            'device_name': parsed_info['device_name'],
            'spec_model': row[0],
            'unit_price': row[1],
            'key_params': parsed_info['key_params']
        }
        yield device

# 模块4：智能解析说明字段
def parse_description(description, remark):
    """解析第5组的说明和备注字段"""
    result = {
        'device_type': None,
        'device_name': None,
        'detection_objects': [],
        'range': None,
        'output_signal': None,
        'display': None,
        'other_features': {}
    }
    
    # 识别设备类型
    if '空气质量' in description:
        result['device_type'] = '空气质量传感器'
    elif 'CO2' in description or '二氧化碳' in description:
        result['device_type'] = 'CO2传感器'
    elif 'CO' in description:
        result['device_type'] = 'CO传感器'
    
    # 提取检测对象
    if '温度' in description:
        result['detection_objects'].append('温度')
    if '湿度' in description:
        result['detection_objects'].append('湿度')
    if 'CO2' in description or '二氧化碳' in description:
        result['detection_objects'].append('CO2')
    if 'PM2.5' in description:
        result['detection_objects'].append('PM2.5')
    if 'PM10' in description:
        result['detection_objects'].append('PM10')
    
    # 提取量程（正则表达式）
    import re
    range_pattern = r'(\d+)-(\d+)\s*(PPM|ppm)'
    range_match = re.search(range_pattern, description)
    if range_match:
        result['range'] = f"{range_match.group(1)}-{range_match.group(2)}"
        result['range_unit'] = range_match.group(3).lower()
    
    # 提取输出信号
    signal_pattern = r'(4-20mA|0-10V|2-10V|Modbus)'
    signals = re.findall(signal_pattern, description)
    if signals:
        result['output_signal'] = '/'.join(signals)
    
    # 提取显示屏信息
    if '带显示' in description or '有显示屏' in description:
        result['display'] = '带显示'
    elif '无显示' in description:
        result['display'] = '无显示'
    
    # 提取其他特征
    if '继电器' in description:
        if '无继电器' in description:
            result['other_features']['继电器'] = '无'
        else:
            result['other_features']['继电器'] = '有'
    
    if '黑色' in description or '白色' in description:
        if '黑色' in description:
            result['other_features']['面板颜色'] = '黑色'
        elif '白色' in description:
            result['other_features']['面板颜色'] = '白色'
    
    return result

# 模块5：生成标准化Excel
def export_standardized_excel(devices, output_file):
    """导出标准化的Excel文件"""
    pass
```

---

## 📝 五、实施步骤

### 第一步：确认基础信息

请确认以下信息：

1. **品牌名称**：
   - 这批传感器的品牌是什么？
   - 是否所有设备都是同一品牌？

2. **默认量程**（用于前4组）：
   - 温度量程：-20~60℃？
   - 湿度量程：0-100%RH？

3. **第5组设备的品牌**：
   - HAQ系列是什么品牌？
   - HSCM、HSCD系列是什么品牌？
   - C6000系列是什么品牌？

### 第二步：运行数据清洗脚本

我将创建完整的数据清洗脚本，包括：
- ✅ 读取5组数据
- ✅ 智能解析第5组
- ✅ 生成key_params
- ✅ 导出标准化Excel
- ✅ 生成导入报告

### 第三步：配置系统

在导入前配置：

1. **添加设备类型关键词**：
```json
{
  "device_type_keywords": [
    "温度传感器",
    "温湿度传感器",
    "CO传感器",
    "CO2传感器",
    "PM传感器",
    "空气质量传感器"
  ]
}
```

2. **添加同义词映射**：
```json
{
  "synonym_map": {
    "温湿度传感器": ["温度湿度传感器", "温湿度探头"],
    "co2传感器": ["二氧化碳传感器", "co2探测器"],
    "co传感器": ["一氧化碳传感器", "co探测器"],
    "pm传感器": ["颗粒物传感器", "pm2.5传感器"],
    "空气质量传感器": ["空气监测仪", "环境监测传感器"]
  }
}
```

3. **更新白名单特征**：
```json
{
  "whitelist_features": [
    "水", "气", "阀",
    "co", "co2", "pm2.5", "pm10",
    "温度", "湿度", "颗粒物",
    "4-20ma", "0-10v", "2-10v", "modbus",
    "ntc", "pt1000", "电子式"
  ]
}
```

### 第四步：批量导入

1. 使用清洗后的标准化Excel
2. 通过系统批量导入功能上传
3. 系统自动生成匹配规则
4. 验证导入结果

---

## 📊 六、预期结果

### 设备库统计

| 设备类型 | 数量 | 占比 |
|---------|------|------|
| 温度传感器 | 14条 | 10.2% |
| 温湿度传感器 | 88条 | 64.2% |
| CO2传感器 | 18条 | 13.1% |
| CO传感器 | 12条 | 8.8% |
| 空气质量传感器 | 4条 | 2.9% |
| 其他 | 1条 | 0.7% |
| **总计** | **137条** | **100%** |

### 数据质量

- ✅ 前4组（102条）：数据质量优秀，直接转换
- ⚠️ 第5组（35条）：需要智能解析，准确率预计95%+

---

## 🚀 七、下一步行动

请回答以下问题，我将立即创建完整的数据清洗脚本：

### 必答问题

1. **品牌信息**：
   - 前4组（HST、HSH系列）的品牌是？
   - 第5组（HAQ、HSCM、HSCD、C6000系列）的品牌是？

2. **默认量程**：
   - 温度量程：-20~60℃？
   - 湿度量程：0-100%RH？

3. **是否需要立即生成清洗脚本**？

### 可选问题

4. 是否需要为第5组的设备添加更多解析规则？
5. 是否需要生成导入模板供手动调整？

---

**报告创建时间**: 2026-03-06  
**分析人员**: Kiro AI  
**数据来源**: data/室内温湿度传感器价格表.xlsx  
**版本**: v2.0（5组数据完整版）
