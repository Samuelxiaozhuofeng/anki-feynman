# 费曼学习插件重构计划

## 背景

当前`gui/review_window.py`文件过于臃肿（约1300行代码），包含了多个不同功能的类和组件，这导致代码难以维护和扩展。本重构计划旨在将此文件拆分为多个独立的模块，提高代码的可维护性和可读性。

## 现状分析

`review_window.py`当前包含以下主要组件：

1. `ClozeDialog` - 填空卡制作对话框
2. `FeynmanReviewDialog` - 费曼学习复习对话框
3. `FollowUpQuestionWorker` - 追加问题处理的工作线程

这些组件都相互耦合，共享大量样式和功能代码，特别是样式代码重复出现在多个地方。

## 重构目标

1. 将各个组件分离为独立模块
2. 提取共用的样式和功能到独立模块
3. 降低组件之间的耦合度
4. 优化代码结构，提高可维护性
5. 保持现有功能不变

## 重构计划

### 第一阶段：创建目录结构

1. 创建合适的目录结构，整理组件和功能：
   - `gui/components/` - 存放UI组件
   - `gui/dialogs/` - 存放对话框组件
   - `gui/styles/` - 存放样式相关代码
   - `gui/workers/` - 存放工作线程相关代码
   - `gui/controllers/` - 存放控制器逻辑

### 第二阶段：提取公共样式

1. 创建 `gui/styles/anki_style.py`：
   - 提取当前重复的样式代码
   - 创建通用的样式生成函数
   - 添加夜间模式支持

### 第三阶段：提取工作线程类

1. 创建 `gui/workers/followup_worker.py`：
   - 移动 `FollowUpQuestionWorker` 到独立文件
   - 优化其接口和异常处理

### 第四阶段：拆分组件

1. 创建 `gui/dialogs/cloze_dialog.py`：
   - 移动 `ClozeDialog` 类到独立文件
   - 引用公共样式
   - 优化其接口

2. 拆分 `FeynmanReviewDialog` 到多个文件：
   - `gui/dialogs/review_dialog.py` - 主对话框框架
   - `gui/components/question_view.py` - 问题显示组件
   - `gui/components/answer_input.py` - 答案输入组件
   - `gui/components/feedback_view.py` - 反馈显示组件
   - `gui/components/followup_panel.py` - 追加提问面板

### 第五阶段：创建控制器

1. 创建 `gui/controllers/review_controller.py`：
   - 分离业务逻辑和UI代码
   - 处理数据流和状态管理
   - 协调各组件之间的交互

### 第六阶段：重构主文件

1. 重新实现 `gui/review_window.py`：
   - 变为导入和组装各组件的入口点
   - 负责初始化和配置组件
   - 最小化代码量和复杂度

## 详细任务清单

### 阶段一：创建目录结构

- [x] 创建必要的子目录
- [x] 准备好基础的空文件

### 阶段二：提取公共样式

- [x] 创建 `gui/styles/anki_style.py`
- [x] 实现 `get_anki_style(night_mode=False)` 函数
- [x] 优化夜间模式检测逻辑

### 阶段三：提取工作线程类

- [x] 创建 `gui/workers/followup_worker.py`
- [x] 移植 `FollowUpQuestionWorker` 类
- [x] 完善信号和异常处理

### 阶段四：拆分对话框和组件

- [x] 创建 `gui/dialogs/cloze_dialog.py`
- [x] 创建 `gui/dialogs/review_dialog.py`
- [x] 创建 `gui/components/question_view.py`
- [x] 创建 `gui/components/answer_input.py`
- [x] 创建 `gui/components/feedback_view.py`
- [x] 创建 `gui/components/followup_panel.py`

### 阶段五：创建控制器

- [x] 创建 `gui/controllers/review_controller.py`
- [x] 实现状态管理和业务逻辑
- [x] 创建 `gui/workers/evaluate_answer_worker.py`
- [x] 测试控制器功能

### 阶段六：重构主文件

- [x] 重新实现 `gui/review_window.py`
- [x] 测试整体集成功能
- [ ] 优化性能和资源使用

## 模块职责定义

### gui/styles/anki_style.py
- 负责提供与Anki风格一致的样式表
- 检测和适配Anki的夜间模式
- 提供一致的UI风格函数

### gui/workers/followup_worker.py
- 在独立线程中处理AI追加问题请求
- 管理上下文和模型切换
- 提供信号机制用于通知UI

### gui/dialogs/cloze_dialog.py
- 提供填空卡创建界面
- 允许用户编辑和标记填空
- 处理填空卡的保存逻辑

### gui/dialogs/review_dialog.py
- 提供主复习界面框架
- 集成和组织各个UI组件
- 管理整体窗口生命周期

### gui/components/question_view.py
- 显示当前问题
- 处理问题格式化
- 支持选择题和问答题不同显示

### gui/components/answer_input.py
- 提供答案输入界面
- 支持选择题选项和问答题文本输入
- 处理答案验证

### gui/components/feedback_view.py
- 显示AI反馈内容
- 格式化反馈信息
- 提取掌握程度信息

### gui/components/followup_panel.py
- 提供追加提问界面
- 管理提问历史显示
- 处理右键菜单操作

### gui/controllers/review_controller.py
- 协调各组件间的数据流
- 管理问题和答案状态
- 处理卡片保存和生成逻辑

## 实施注意事项

1. 在重构过程中保持功能不变
2. 每个阶段完成后进行测试，确保没有引入新问题
3. 注意处理组件间的依赖关系，避免循环引用
4. 优化导入语句，避免不必要的导入
5. 保持一致的编码风格和命名规范
6. 添加适当的注释和文档

## 预期收益

1. 提高代码可维护性和可读性
2. 便于未来新功能的开发和扩展
3. 降低维护成本
4. 优化界面加载和响应速度
5. 更好的组件复用性

## 进度跟踪

- [x] 阶段一完成
- [x] 阶段二完成
- [x] 阶段三完成
- [x] 阶段四完成
- [x] 阶段五完成
- [x] 阶段六完成
- [x] 整体测试通过 