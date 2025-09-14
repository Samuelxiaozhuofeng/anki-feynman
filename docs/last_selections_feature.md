# 上次选择记忆功能

## 功能概述

这个功能允许插件自动记忆用户在"知识输入"窗口中的上次选择，包括：

- 选择的牌组
- 问题类型
- 模板选择
- 问题数量
- AI模型选择
- 追问模型选择

当用户下次打开知识输入窗口时，这些选择会自动恢复到上次的状态。

## 实现原理

### 1. 配置存储

在 `config.json` 中添加了 `last_selections` 部分：

```json
{
  "last_selections": {
    "deck": "",
    "question_type": "",
    "template": "",
    "num_questions": 5,
    "model": "",
    "followup_model": ""
  }
}
```

### 2. 核心文件修改

#### `gui/input_window.py`

- 添加了 `load_last_selections()` 方法：在窗口显示时加载上次的选择
- 添加了 `save_current_selections()` 方法：保存当前的选择到配置文件
- 添加了 `_initializing` 标志：防止在初始化过程中触发保存操作

#### `gui/controllers/input_events_controller.py`

- 在 `setup_connections()` 中为所有相关控件添加了变更事件监听
- 添加了 `on_selection_changed()` 方法：当用户改变选择时自动保存

### 3. 工作流程

1. **窗口初始化**：
   - 设置 `_initializing = True`
   - 创建UI组件
   - 加载牌组和模型数据
   - 设置事件连接
   - 调用 `load_last_selections()` 恢复上次选择
   - 设置 `_initializing = False`

2. **用户操作**：
   - 用户改变任何选择（牌组、问题类型等）
   - 触发相应的变更事件
   - 调用 `on_selection_changed()`
   - 自动保存当前选择到配置文件

3. **下次打开**：
   - 重复步骤1，自动恢复上次的选择

## 技术细节

### 防护机制

1. **初始化保护**：使用 `_initializing` 标志防止在窗口初始化时触发保存操作
2. **异常处理**：所有保存和加载操作都包含在 try-catch 块中
3. **存在性检查**：在访问UI控件前检查其是否存在

### 兼容性

- 向后兼容：如果配置文件中没有 `last_selections` 部分，会自动创建
- 控件检查：在操作前检查UI控件是否存在，避免错误

### 性能考虑

- 延迟保存：只在用户实际改变选择时才保存，不会频繁写入文件
- 轻量级操作：保存操作很快，不会影响用户体验

## 使用示例

### 用户场景

1. 用户打开知识输入窗口
2. 选择牌组"英语学习"
3. 选择问题类型"选择题"
4. 设置问题数量为10
5. 关闭窗口
6. 下次打开时，所有选择自动恢复

### 开发者扩展

如果需要添加新的选择项记忆：

1. 在配置文件的 `last_selections` 中添加新字段
2. 在 `load_last_selections()` 中添加加载逻辑
3. 在 `save_current_selections()` 中添加保存逻辑
4. 在 `setup_connections()` 中为新控件添加事件监听

## 测试

运行 `test_last_selections.py` 可以测试功能是否正常工作：

```bash
python test_last_selections.py
```

测试包括：
- 配置文件结构验证
- 保存和加载功能测试
- 数据完整性检查

## 注意事项

1. 配置文件会在每次选择变更时写入，确保数据及时保存
2. 如果某个选择项在下次打开时不存在（如牌组被删除），会跳过该项的恢复
3. 数字类型的选择（如问题数量）会直接设置，字符串类型会通过查找匹配项设置
