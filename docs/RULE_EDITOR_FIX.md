# 规则编辑器功能修复

## 问题描述

用户在规则编辑器页面 (`http://localhost:3000/rule-editor/R_V5011N1040_U000000000000000001`) 遇到两个问题:

1. **保存失败**: 修改特征权重后点击"保存修改"按钮,提示"规则保存失败，请稍后重试"
2. **类型显示错误**: 特征与权重配置中的类型全部显示为"参数",没有正确区分品牌、设备类型、型号等

## 问题分析

### 问题1: 保存失败

**根本原因**: 后端缺少 PUT 路由来更新规则

前端调用:
```javascript
const response = await api.put(`/rules/management/${props.ruleId}`, requestData)
```

但后端只有 GET 路由:
```python
@app.route('/api/rules/management/<rule_id>', methods=['GET'])
```

没有对应的 PUT 路由来处理更新请求,导致返回404或405错误。

### 问题2: 类型显示错误

**根本原因**: 特征类型推断逻辑过于简单

原代码:
```python
feature_type = 'parameter'  # 默认类型
if '品牌' in feature or feature == target_rule.target_device_id.split('_')[0]:
    feature_type = 'brand'
elif '型号' in feature or 'model' in feature.lower():
    feature_type = 'model'
elif '设备' in feature or 'device' in feature.lower():
    feature_type = 'device_type'
```

问题:
- 只检查特征名称中是否包含"品牌"、"型号"等关键词
- 没有利用配置文件中的 `brand_keywords` 和 `device_type_keywords`
- 没有与设备信息进行对比
- 导致大部分特征都被识别为"参数"

## 修复方案

### 1. 添加 PUT 路由

**文件**: `backend/app.py`

```python
@app.route('/api/rules/management/<rule_id>', methods=['PUT'])
def update_rule(rule_id):
    """更新规则接口"""
    try:
        data = request.get_json()
        
        # 检查数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return jsonify(create_error_response('NOT_DATABASE_MODE', 
                '当前不是数据库模式，无法更新规则')), 400
        
        # 获取现有规则
        all_rules = data_loader.get_all_rules()
        target_rule = None
        for rule in all_rules:
            if rule.rule_id == rule_id:
                target_rule = rule
                break
        
        if not target_rule:
            return jsonify(create_error_response('RULE_NOT_FOUND', 
                f'规则不存在: {rule_id}')), 404
        
        # 更新规则数据
        if 'match_threshold' in data:
            target_rule.match_threshold = float(data['match_threshold'])
        
        if 'features' in data:
            # 重建feature_weights字典
            new_feature_weights = {}
            for feature_item in data['features']:
                feature_name = feature_item['feature']
                feature_weight = float(feature_item['weight'])
                new_feature_weights[feature_name] = feature_weight
            
            target_rule.feature_weights = new_feature_weights
            target_rule.auto_extracted_features = list(new_feature_weights.keys())
        
        # 保存到数据库
        success = data_loader.loader.save_rule(target_rule)
        
        if success:
            # 重新加载规则到内存
            global match_engine
            rules = data_loader.load_rules()
            devices = data_loader.load_devices()
            config = data_loader.load_config()
            match_engine = MatchEngine(rules=rules, devices=devices, config=config)
            
            return jsonify({'success': True, 'message': '规则更新成功'})
        else:
            return jsonify(create_error_response('UPDATE_RULE_ERROR', 
                '规则更新失败')), 500
        
    except Exception as e:
        logger.error(f"更新规则失败: {e}")
        return jsonify(create_error_response('UPDATE_RULE_ERROR', 
            '更新规则失败', {'error_detail': str(e)})), 500
```

### 2. 改进特征类型推断

**新增辅助函数**:

```python
def _infer_feature_type(feature, device=None):
    """
    推断特征类型
    
    Args:
        feature: 特征名称
        device: 设备对象（可选）
        
    Returns:
        特征类型: 'brand', 'device_type', 'model', 'parameter'
    """
    feature_lower = feature.lower()
    
    # 加载配置
    config = data_loader.load_config()
    brand_keywords = config.get('brand_keywords', [])
    device_type_keywords = config.get('device_type_keywords', [])
    
    # 1. 检查是否是品牌
    if device and feature == device.brand:
        return 'brand'
    
    for brand in brand_keywords:
        if brand.lower() == feature_lower or brand.lower() in feature_lower:
            return 'brand'
    
    # 2. 检查是否是设备类型
    for device_type in device_type_keywords:
        if device_type.lower() == feature_lower or device_type.lower() in feature_lower:
            return 'device_type'
    
    # 3. 检查是否是型号
    if device and feature == device.spec_model:
        return 'model'
    
    # 包含型号特征的关键词
    model_indicators = ['v5', 'ml', 'ddc', 'vav', 'ahu', 'fcu']
    for indicator in model_indicators:
        if indicator in feature_lower:
            return 'model'
    
    # 4. 默认为参数
    return 'parameter'
```

**更新 GET 路由**:

```python
# 将特征和权重转换为前端期望的格式，并添加类型信息
features = []
for feature, weight in target_rule.feature_weights.items():
    # 使用改进的类型推断函数
    feature_type = _infer_feature_type(feature, target_device)
    
    features.append({
        'feature': feature,
        'weight': weight,
        'type': feature_type
    })
```

## 验证结果

### API测试

```bash
python backend/test_rule_update_api.py
```

**测试结果**:
```
================================================================================
测试规则更新API - R_V5011N1040_U000000000000000001
================================================================================

步骤1: 获取规则详情
  ✓ 规则获取成功
  规则ID: R_V5011N1040_U000000000000000001
  匹配阈值: 5.0
  特征数量: 9

  前5个特征:
    1. 霍尼韦尔 - 权重: 1 - 类型: brand
    2. 座阀 - 权重: 2.5 - 类型: device_type
    3. 二通 - 权重: 4 - 类型: parameter
    4. dn15 - 权重: 1 - 类型: parameter
    5. 水 - 权重: 4 - 类型: parameter

步骤2: 修改规则
  修改特征 '霍尼韦尔' 的权重: 1 -> 1.5
  修改匹配阈值: 5.0 -> 5.5

步骤3: 保存修改
  ✓ 规则更新成功!

步骤4: 验证更新
  ✓ 验证成功
  新匹配阈值: 5.5
  新特征权重: 1.5

================================================================================
✓ 测试通过!
================================================================================
```

### 前端测试

1. 打开规则编辑器页面: `http://localhost:3000/rule-editor/R_V5011N1040_U000000000000000001`
2. 查看特征类型显示:
   - ✅ "霍尼韦尔" 显示为 "品牌"
   - ✅ "座阀" 显示为 "设备类型"
   - ✅ 其他参数显示为 "参数"
3. 修改特征权重
4. 点击"保存修改"
5. ✅ 提示"规则保存成功"
6. 刷新页面验证修改已保存

## 特征类型识别逻辑

### 优先级

1. **品牌** (brand)
   - 与设备品牌字段完全匹配
   - 在配置的 `brand_keywords` 列表中

2. **设备类型** (device_type)
   - 在配置的 `device_type_keywords` 列表中
   - 例如: "座阀"、"传感器"、"控制器"

3. **型号** (model)
   - 与设备规格型号字段完全匹配
   - 包含型号特征关键词: v5, ml, ddc, vav, ahu, fcu

4. **参数** (parameter)
   - 默认类型
   - 其他所有特征

### 配置依赖

特征类型识别依赖于配置文件中的:
- `brand_keywords`: 品牌关键词列表
- `device_type_keywords`: 设备类型关键词列表

确保这些配置正确维护以获得准确的类型识别。

## 修改文件清单

1. `backend/app.py` - 添加 PUT 路由和改进类型推断
2. `backend/test_rule_update_api.py` - 新增API测试脚本

## API文档

### PUT /api/rules/management/<rule_id>

更新指定规则

**请求体**:
```json
{
  "match_threshold": 5.5,
  "features": [
    {
      "feature": "霍尼韦尔",
      "weight": 1.5
    },
    {
      "feature": "座阀",
      "weight": 2.5
    }
  ],
  "remark": "可选备注"
}
```

**响应**:
```json
{
  "success": true,
  "message": "规则更新成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "error_code": "RULE_NOT_FOUND",
  "error_message": "规则不存在: R_xxx"
}
```

## 注意事项

1. **数据库模式**: 此功能仅在数据库存储模式下可用
2. **内存更新**: 规则更新后会自动重新加载匹配引擎
3. **特征验证**: 前端会验证特征名称不能为空且不能重复
4. **权重范围**: 权重值范围为 0-10,精度为0.1
5. **阈值范围**: 匹配阈值范围为 0-100,精度为0.1

## 相关文档

- [配置管理用户指南](./CONFIG_MANAGEMENT_USER_GUIDE.md)
- [规则管理用户手册](./RULE_MANAGEMENT_USER_MANUAL.md)
- [特征提取优化总结](./FEATURE_EXTRACTION_OPTIMIZATION_SUMMARY.md)
