# Anki Feynman Learning 插件打包工具使用指南

## 📋 目录

- [快速开始](#快速开始)
- [详细步骤](#详细步骤)
- [文件说明](#文件说明)
- [常见问题](#常见问题)
- [高级配置](#高级配置)

## 🚀 快速开始

### 第一步：安装依赖（首次使用）

```bash
# Windows 用户
双击运行: 安装依赖.bat

# 或手动运行
pip install -r requirements.txt -t vendor --upgrade
```

### 第二步：打包插件

```bash
# Windows 用户
双击运行: 打包插件.bat

# 或手动运行
python build_addon.py
```

### 第三步：分发

打包后的文件在 `dist/` 目录下，文件名格式：
```
anki_feynman_YYYYMMDD_HHMMSS.ankiaddon
```

将此文件发送给其他用户即可。

## 📝 详细步骤

### 1. 环境要求

- Python 3.7 或更高版本
- pip（Python 包管理器）
- Windows 10/11（脚本针对 Windows 优化）

### 2. 安装依赖库

**为什么需要这一步？**

插件依赖一些外部库（如 OpenAI、aiohttp 等），这些库需要打包到 `vendor` 目录中，才能在其他用户的电脑上正常运行。

**操作方法：**

```bash
# 方法一：使用批处理文件（推荐）
双击 安装依赖.bat

# 方法二：命令行
pip install -r requirements.txt -t vendor --upgrade
```

**安装的依赖包括：**
- openai==0.28.0
- aiohttp>=3.8.0
- async-timeout>=4.0.0
- requests>=2.20
- tqdm>=4.0
- pypdf>=3.0.0
- typing_extensions>=4.0.0

### 3. 打包插件

**操作方法：**

```bash
# 方法一：使用批处理文件（推荐）
双击 打包插件.bat

# 方法二：命令行
python build_addon.py
```

**打包过程会：**
1. ✅ 收集所有必要的文件
2. ✅ 包含 vendor 目录中的所有依赖
3. ✅ 自动清除 config.json 中的 API keys
4. ✅ 排除开发文件和临时文件
5. ✅ 生成 .ankiaddon 文件

### 4. 验证打包结果

打包成功后，你会看到类似输出：

```
============================================================
打包完成！
============================================================
输出文件: C:\...\dist\anki_feynman_20251114_110114.ankiaddon
文件大小: 1.72 MB (1,807,559 bytes)

安装说明:
1. 打开 Anki
2. 工具 -> 插件 -> 从文件安装
3. 选择文件: anki_feynman_20251114_110114.ankiaddon
4. 重启 Anki
============================================================
```

## 📁 文件说明

### 核心文件

| 文件名 | 说明 |
|--------|------|
| `build_addon.py` | 打包脚本（核心） |
| `打包插件.bat` | Windows 快捷打包脚本 |
| `安装依赖.bat` | Windows 快捷安装依赖脚本 |
| `requirements.txt` | 依赖列表 |
| `打包说明.md` | 详细打包说明 |
| `README_打包工具.md` | 本文件 |

### 生成的文件

| 位置 | 说明 |
|------|------|
| `dist/*.ankiaddon` | 打包后的插件文件 |
| `dist/temp_build/` | 临时构建目录（自动清理） |

## ❓ 常见问题

### Q1: 打包后朋友安装时报错 "ModuleNotFoundError: No module named 'xxx'"

**原因：** 缺少依赖库。

**解决方案：**
1. 运行 `安装依赖.bat` 或 `pip install -r requirements.txt -t vendor --upgrade`
2. 重新打包

### Q2: 如何确认 API key 已被清除？

**验证方法：**
```bash
# 解压 .ankiaddon 文件（它是 zip 格式）
# 查看 config.json 文件
# api_key 字段应该为空字符串 ""
```

或使用 Python 验证：
```python
import zipfile, json
z = zipfile.ZipFile('dist/anki_feynman_XXXXXX.ankiaddon')
data = json.loads(z.read('config.json'))
print('OpenAI API Key:', data['ai_service']['openai']['api_key'])
print('Custom API Key:', data['ai_service']['custom']['api_key'])
# 输出应该都是空字符串
```

### Q3: 打包文件太大怎么办？

**当前大小：** 约 1.7 MB

**如果需要减小：**
1. 检查 vendor 目录，删除不必要的测试文件
2. 在 `build_addon.py` 中添加更多排除规则

### Q4: 如何在 macOS 或 Linux 上使用？

**方法：**
```bash
# 安装依赖
pip3 install -r requirements.txt -t vendor --upgrade

# 打包
python3 build_addon.py
```

### Q5: 打包后的插件在其他电脑上无法运行

**检查清单：**
- [ ] 是否安装了所有依赖到 vendor 目录？
- [ ] 对方的 Anki 版本是否兼容（需要 2.1.50+）？
- [ ] 对方的 Python 版本是否兼容（Anki 内置）？
- [ ] 查看 Anki 的错误日志获取详细信息

## 🔧 高级配置

### 修改打包内容

编辑 `build_addon.py` 中的配置：

```python
# 添加要包含的文件
INCLUDE_PATTERNS = [
    "__init__.py",
    "manifest.json",
    # 添加更多...
]

# 添加要排除的文件
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    # 添加更多...
]
```

### 添加敏感信息清理

```python
SENSITIVE_FILES = {
    "config.json": [
        "ai_service.openai.api_key",
        "ai_service.custom.api_key"
    ],
    # 添加其他需要清理的文件
}
```

## 📦 分发给其他用户

### 安装步骤（给用户）

1. 下载 `.ankiaddon` 文件
2. 打开 Anki
3. 点击 **工具** → **插件**
4. 点击 **从文件安装**
5. 选择下载的 `.ankiaddon` 文件
6. 重启 Anki
7. 在插件设置中配置 API key

### 注意事项

⚠️ **重要提醒：**
- 打包后的文件不包含 API key，用户需要自行配置
- 首次使用需要在设置中输入 OpenAI 或自定义 API 的密钥
- 建议提供配置说明文档

## 🛠️ 故障排除

### 问题：pip install 失败

**解决方案：**
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -t vendor -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题：打包脚本运行失败

**检查：**
1. Python 版本是否 >= 3.7
2. 是否有文件被占用（关闭 Anki）
3. 是否有足够的磁盘空间

## 📞 获取帮助

如果遇到问题：
1. 查看错误信息
2. 检查本文档的常见问题部分
3. 查看 Anki 的错误日志
4. 联系开发者

## 📄 许可证

本打包工具遵循与主项目相同的许可证。

