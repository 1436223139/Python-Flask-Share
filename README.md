# Python Flask 局域网文件分享工具

一个基于 Python Flask 的个人文件服务器，提供现代化的网页界面用于在局域网内分享和管理文件。

## 🌟 特性

- 现代化、响应式的网页界面
- 支持文件上传、下载、预览和删除
- 支持批量操作（批量下载、批量删除）
- 全局文件搜索功能
- 支持设置访问密码保护
- 支持文件夹浏览和导航
- 支持文本文件在线预览
- 支持图片文件在线预览
- 完全离线运行，无需外网连接

## 📋 系统要求

- Windows 7 或更高版本
- Python 3.6 或更高版本

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd Python-Flask-Share
```

### 2. 创建虚拟环境

```bash
python -m venv venv
```

### 3. 激活虚拟环境

```bash
# Windows CMD
venv\Scripts\activate

# Windows PowerShell
venv\Scripts\Activate.ps1
```

### 4. 安装依赖

在线安装：
```bash
pip install flask Flask-Dropzone
```

离线安装（推荐）：
```bash
# 项目已包含所有必需的wheel文件，直接安装
pip install --find-links wheels --no-index flask Flask-Dropzone
```

### 5. 启动服务

双击运行 `启动器.bat` 文件，按照交互式菜单提示进行操作：

1. 选择运行模式（前台运行/后台运行）
2. 设置共享目录（默认为程序目录下的 shared 文件夹）
3. 设置端口号（默认为 5000）
4. 设置访问密码（可选）

启动成功后，可以在浏览器中访问 `http://localhost:5000`（或你设置的其他端口）来使用文件服务器。

## 📁 项目结构

```
Python-Flask-Share/
│
├── 启动器.bat                  <-- 唯一的启动入口
├── server.py                   <-- 核心后端应用
├── requirements.txt            <-- 依赖包列表
├── wheels/                     <-- 离线安装包 (包含所有依赖的wheel文件)
├── templates/                  <-- 存放所有 HTML 页面
│   ├── index.html
│   ├── login.html
│   └── search_results.html
├── static/                     <-- 存放所有静态资源 (CSS/JS/图标)
│   ├── css/
│   │   ├── dropzone.min.css
│   │   └── fancybox.css
│   └── js/
│       ├── dropzone.min.js
│       ├── fancybox.umd.js
│       └── feather.min.js
└── venv/                       <-- Python 虚拟环境 (需要自己创建)
```

## ⚙️ 个性化配置

可以通过修改以下文件中的配置来自定义服务器：

| 功能            | 所在文件          | 配置位置 |
| :-------------- | :---------------- | :------- |
| 默认共享目录     | `启动器.bat`      | `SHARE_FOLDER_DEFAULT` |
| 默认端口        | `启动器.bat`      | `PORT_DEFAULT` |
| 默认密码        | `启动器.bat`      | `PASSWORD_DEFAULT` |
| 登录有效期      | `server.py`       | `app.permanent_session_lifetime` |
| 会话安全密钥    | `server.py`       | `app.secret_key` |
| UI 主题颜色     | `templates/index.html` | `:root` 中的 `--primary-color` |
| UI 背景颜色     | `templates/index.html` | `:root` 中的 `--background-color` |

## 📝 使用说明

1. 访问服务器地址后，可以看到文件浏览界面
2. 左侧边栏支持文件拖拽上传和创建新文件夹
3. 主界面支持：
   - 文件/文件夹浏览
   - 排序（按名称、大小、修改日期）
   - 批量选择和操作
   - 全局搜索
   - 文件预览（文本和图片）
4. 支持多选文件后进行批量下载或删除操作

## 🔒 安全说明

- 可以设置访问密码保护服务器
- 程序具有基础的路径遍历攻击防护
- 会话管理确保用户登录状态安全

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 📄 许可证

本项目仅供个人学习和使用，请勿用于商业用途。