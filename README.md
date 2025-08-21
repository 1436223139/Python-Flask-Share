
---

### **🚀 个人文件服务器 - 最终部署方案**

#### **一、 项目简介**

这是一个基于 Python Flask、完全离线运行的个人文件服务器。它提供了一个现代、美观的网页界面，支持所有基础文件操作、批量处理、文件预览、全局搜索和密码保护，并通过一个强大的交互式启动器在 Windows 环境下轻松运行。

#### **二、 最终项目文件结构**

请确保您的项目根目录（例如 `Python-Flask-Share`）下包含以下所有文件和文件夹，结构要完全一致：

```
Python-Flask-Share/
│
├── 启动器.bat                  <-- 唯一的启动入口
│
├── server.py                   <-- 核心后端应用
│
├── templates/                  <-- 存放所有 HTML 页面
│   ├── index.html
│   ├── login.html
│   └── search_results.html
│
├── static/                     <-- 存放所有静态资源 (CSS/JS/图标)
│   ├── css/
│   │   ├── dropzone.min.css
│   │   └── fancybox.css
│   └── js/
│       ├── dropzone.min.js
│       ├── fancybox.umd.js
│       └── feather.min.js
│
└── venv/                       <-- Python 虚拟环境 (自动生成)
    ├── ... (许多文件和文件夹)
```

#### **三、 从零开始部署步骤**

假设您在一台全新的、已安装 Python 的 Windows 电脑上进行部署。

**步骤 1：准备环境**

1.  **安装 Python**: 确保系统已安装 Python 3.6 或更高版本。
2.  **创建项目文件夹**: 创建一个项目根文件夹，例如 `C:\MyFileServer`。
3.  **创建虚拟环境**:
    *   打开命令提示符 (CMD)，进入该文件夹：`cd C:\MyFileServer`
    *   运行命令创建虚拟环境：`python -m venv venv`
4.  **激活虚拟环境**:
    *   运行激活命令：`venv\Scripts\activate`
    *   激活后，您会看到命令行前面有 `(venv)` 字样。
5.  **安装依赖**:
    *   在激活的环境中，需要安装2个库——Flask、Flask-Dropzone：`pip install flask Flask-Dropzone`

**步骤 2：放置项目文件**

将下面提供的所有代码，按照第二节的“文件结构”图，创建相应的文件并粘贴进去。

**1. `启动器.bat` (放置在根目录)**
```batch
@echo off
REM 切换代码页以正确处理中文字符
chcp 65001 > nul
setlocal

REM 设置窗口标题
title 文件服务器启动器 V3.0

REM ==================================================================
REM               --- 默认配置区 ---
REM
REM 您可以在这里修改默认的共享目录、端口和密码。
REM ==================================================================
set "SHARE_FOLDER_DEFAULT=%~dp0shared"
set "PORT_DEFAULT=5000"
set "PASSWORD_DEFAULT="

:menu
cls
echo.
echo  ========================================================
echo                 个人文件服务器 启动器 V3.0
echo  ========================================================
echo.
echo   [1] 前台运行 (窗口关闭则服务停止, 可看日志)
echo.
echo   [2] 后台运行 (无窗口, 需在任务管理器中关闭)
echo.
echo   [3] 退出
echo.
echo  ========================================================
echo.

choice /c 123 /n /m "请输入选项 [1, 2, 3]: "

if errorlevel 3 goto :exit
if errorlevel 2 goto :start_background
if errorlevel 1 goto :start_foreground

echo.
echo 无效输入，请重新选择。
timeout /t 1 > nul
goto :menu

:start_foreground
call :get_params
cls
echo.
echo 准备在前台启动服务器...
echo.
echo   分享目录: %SHARE_FOLDER%
echo   端口: %PORT%
if defined PASSWORD (echo   密码: 已设置) else (echo   密码: 未设置)
echo.
echo 按下 CTRL+C 可以关闭服务并返回主菜单。
echo.

if defined PASSWORD (
    venv\Scripts\python.exe server.py "%SHARE_FOLDER%" --port %PORT% --password "%PASSWORD%"
) else (
    venv\Scripts\python.exe server.py "%SHARE_FOLDER%" --port %PORT%
)

echo.
echo 服务已停止。
pause
goto :menu

:start_background
call :get_params
cls
echo.
echo 准备在后台启动服务器...
echo.
echo   分享目录: %SHARE_FOLDER%
echo   端口: %PORT%
if defined PASSWORD (echo   密码: 已设置) else (echo   密码: 未设置)
echo.

if defined PASSWORD (
    start "Python File Server Background" venv\Scripts\pythonw.exe server.py "%SHARE_FOLDER%" --port %PORT% --password "%PASSWORD%"
) else (
    start "Python File Server Background" venv\Scripts\pythonw.exe server.py "%SHARE_FOLDER%" --port %PORT%
)

echo 服务器已在后台启动！
echo.
echo 如需关闭, 请打开任务管理器, 找到 "pythonw.exe" 进程并结束它。
echo.
echo 3秒后返回主菜单...
timeout /t 3 > nul
goto :menu

:get_params
cls
echo.
echo --- 参数设置 ---
echo.

set "SHARE_FOLDER="
set /p SHARE_FOLDER="请输入要分享的目录 (留空使用默认: %SHARE_FOLDER_DEFAULT%): "
if not defined SHARE_FOLDER set "SHARE_FOLDER=%SHARE_FOLDER_DEFAULT%"

REM 确保如果默认目录不存在则创建它
if not exist "%SHARE_FOLDER%" (
    echo.
    echo 警告: 目录 "%SHARE_FOLDER%" 不存在, 将自动创建。
    mkdir "%SHARE_FOLDER%" > nul
)

echo.
set "PORT="
set /p PORT="请输入端口号 (留空使用默认: %PORT_DEFAULT%): "
if not defined PORT set "PORT=%PORT_DEFAULT%"

echo.
set "PASSWORD="
set /p PASSWORD="请输入访问密码 (留空表示不设密码, 默认: %PASSWORD_DEFAULT%): "
if not defined PASSWORD set "PASSWORD=%PASSWORD_DEFAULT%"
echo.
goto :eof

:exit
exit /b
```

**2. `server.py` (放置在根目录)**
```python
# 此处粘贴完整的 server.py 代码
# （代码与上一条回复中的完全相同，为保持方案完整性，理论上应全部粘贴于此）
# （为了简洁，此处省略，请使用上一条回复中提供的最终版 server.py）
```

**3. `templates/index.html`**
```html
# 此处粘贴完整的 index.html 代码
# （同上，请使用上一条回复中提供的最终版 index.html）
```

**4. `templates/login.html`**
```html
# 此处粘贴完整的 login.html 代码
# （同上，请使用上一条回复中提供的最终版 login.html）
```

**5. `templates/search_results.html`**
```html
# 此处粘贴完整的 search_results.html 代码
# （同上，请使用上一条回复中提供的最终版 search_results.html）
```

**步骤 3：下载并放置离线静态资源**

这是确保服务器**完全离线**运行的关键。请下载以下文件并放入对应的 `static` 文件夹内。
*   **Feather Icons**:
    *   下载地址: `https://unpkg.com/feather-icons`
    *   找到 `dist/feather.min.js` 文件。
    *   放入: `static/js/feather.min.js`
*   **FancyBox**:
    *   下载地址: `https://cdn.jsdelivr.net/npm/@fancyapps/ui@5.0/dist/`
    *   下载 `fancybox.umd.js` -> 放入 `static/js/`
    *   下载 `fancybox.css` -> 放入 `static/css/`
*   **Dropzone**:
    *   下载地址: `https://unpkg.com/dropzone@5/dist/min/`
    *   下载 `dropzone.min.js` -> 放入 `static/js/`
    *   下载 `dropzone.min.css` -> 放入 `static/css/`

**步骤 4：运行！**

双击 `启动器.bat`，即可看到交互式菜单，按提示操作即可启动服务。

---

### **⚙️ 个性化与自定义指南**

您可以轻松修改以下变量来定制您的服务器，无需深入代码。

| 功能            | 所在文件          | 如何修改                                                                  | 描述                                                                                                             |
| :-------------- | :---------------- | :------------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------- |
| **默认共享目录**  | `启动器.bat`      | 修改 `set "SHARE_FOLDER_DEFAULT=..."` 的值为您的路径，如 `D:\Downloads`。 | 启动器在不输入任何内容时，默认使用的共享文件夹路径。                                                               |
| **默认端口**      | `启动器.bat`      | 修改 `set "PORT_DEFAULT=5000"` 的值为您想要的端口，如 `8888`。                | 服务器运行时监听的网络端口。                                                                                     |
| **默认密码**      | `启动器.bat`      | 修改 `set "PASSWORD_DEFAULT=..."` 的值为您的密码，如 `admin`。留空则默认无密码。 | 启动器在不输入任何内容时，默认设置的访问密码。                                                                   |
| **登录有效期**    | `server.py`       | 修改 `app.permanent_session_lifetime = datetime.timedelta(days=7)` 的天数。 | 用户登录一次后，保持登录状态的时间。                                                                             |
| **会话安全密钥**  | `server.py`       | 修改 `app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'` 为任意复杂的字节字符串。      | 用于加密用户会话信息，更改它可以让旧的登录凭证失效。                                                             |
| **UI 主题颜色**   | `templates/index.html` | 在 `<style>` 标签内，修改 `:root` 中的 `--primary-color` 的值，如 `#ff6347`。 | 控制界面中所有链接、按钮和图标的主要颜色。                                                                       |
| **UI 背景颜色**   | `templates/index.html` | 在 `<style>` 标签内，修改 `:root` 中的 `--background-color` 的值，如 `#ffffff`。 | 控制页面的主要背景色。                                                                                           |
| **UI 文件夹颜色** | `templates/index.html` | 在 `<style>` 标签内，修改 `:root` 中的 `--folder-icon-color` 的值。       | 单独控制文件夹图标的颜色。                                                                                       |
| **UI 文件颜色**   | `templates/index.html` | 在 `<style>` 标签内，修改 `:root` 中的 `--file-icon-color` 的值。         | 单独控制文件图标的颜色。                                                                                         |

---

至此，您的个人文件服务器项目不仅功能完善，而且拥有了清晰的部署和维护文档。再次祝贺您成功完成这个杰出的项目！如果您未来有任何新的想法，我们随时可以继续探索。