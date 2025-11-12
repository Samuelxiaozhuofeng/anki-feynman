# Knowledge Window 键盘快捷键功能

## 功能概述

为 Knowledge Window（知识卡片窗口）添加了键盘快捷键支持，提升用户浏览和操作效率。

## 新增快捷键

### 1. 卡片导航
- **左箭头键 (←)**: 显示上一张卡片
- **右箭头键 (→)**: 显示下一张卡片

### 2. 快速添加
- **空格键 (Space)**: 添加当前卡片到 Anki 并自动跳转到下一张

## 改进功能

### 1. 非阻塞式提示
- **之前**: 添加卡片后弹出模态对话框 "知识卡已添加到Anki"，需要用户点击确认
- **现在**: 使用 tooltip 提示，1秒后自动消失，不阻塞用户操作

### 2. 自动跳转
- 使用空格键添加卡片后，自动跳转到下一张卡片
- 点击"添加到Anki"按钮仍保持原有行为（不自动跳转）

### 3. 卡片状态追踪
- 记录已添加的卡片索引
- 已添加的卡片按钮显示为 "✓ 已添加"
- 重复添加时显示提示 "此卡片已添加"

### 4. 智能跳转
- 如果当前卡片已添加，按空格键会跳转到下一张（不重复添加）

## 使用场景

### 快速浏览模式
```
用户操作流程：
1. 打开 Knowledge Window
2. 阅读当前卡片
3. 按空格键添加 → 自动跳转到下一张
4. 继续阅读 → 按空格键添加 → 自动跳转
5. 重复步骤 3-4，快速处理所有卡片
```

### 精细浏览模式
```
用户操作流程：
1. 使用左右箭头键浏览卡片
2. 遇到需要添加的卡片，按空格键或点击按钮
3. 继续使用箭头键浏览
```

## 技术实现

### 1. 快捷键绑定
```python
def _setup_shortcuts(self):
    # 左箭头：上一张卡片
    self.shortcut_prev = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
    self.shortcut_prev.activated.connect(self._show_prev_card)
    
    # 右箭头：下一张卡片
    self.shortcut_next = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
    self.shortcut_next.activated.connect(self._show_next_card)
    
    # 空格：添加卡片到Anki
    self.shortcut_add = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
    self.shortcut_add.activated.connect(self._add_to_anki_with_shortcut)
```

### 2. 状态管理
```python
# 初始化时创建已添加卡片集合
self.added_cards = set()

# 添加成功后记录
self.added_cards.add(self.current_index)

# 切换卡片时更新按钮状态
def _update_card_status(self):
    if self.current_index in self.added_cards:
        self.add_button.setText("✓ 已添加")
    else:
        self.add_button.setText("添加到Anki")
```

### 3. 非阻塞提示
```python
# 使用 tooltip 代替 showInfo
tooltip(get_message("knowledge_card_added", self.lang), period=1000, parent=self)
```

## 新增语言消息

### 中文
- `card_added_status`: "✓ 已添加"
- `card_already_added`: "此卡片已添加"

### English
- `card_added_status`: "✓ Added"
- `card_already_added`: "This card has already been added"

## 用户体验提升

1. **效率提升**: 使用键盘快捷键，无需鼠标点击，操作更快
2. **流畅性**: 非阻塞提示，不打断用户操作流程
3. **智能化**: 自动跳转和状态追踪，减少重复操作
4. **可视化**: 按钮状态变化，清晰显示卡片是否已添加

## 兼容性

- 保持原有按钮点击功能不变
- 快捷键不影响追问面板的输入操作
- 支持中英文界面

