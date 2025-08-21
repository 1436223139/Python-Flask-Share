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
set "SHARE_FOLDER_DEFAULT=C:\Users\MouRen\Downloads"
set "PORT_DEFAULT=880"
set "PASSWORD_DEFAULT="

:menu
cls
echo.
echo  [96m========================================================[0m
echo  [96m                个人文件服务器 启动器 V3.0[0m
echo  [96m========================================================[0m
echo.
echo   [92m[1] 前台运行[0m (窗口关闭则服务停止, 可看日志)
echo.
echo   [93m[2] 后台运行[0m (无窗口, 需在任务管理器中关闭)
echo.
echo   [3] 退出
echo.
echo  [96m========================================================[0m
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
echo [92m准备在前台启动服务器...[0m
echo.
echo   分享目录: %SHARE_FOLDER%
echo   端口: %PORT%
if defined PASSWORD (echo   密码: 已设置) else (echo   密码: 未设置)
echo.
echo [93m按下 CTRL+C 可以关闭服务并返回主菜单。[0m
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
echo [93m准备在后台启动服务器...[0m
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

echo [92m服务器已在后台启动！[0m
echo.
echo 如需关闭, 请打开任务管理器, 找到 "pythonw.exe" 进程并结束它。
echo.
echo 3秒后返回主菜单...
timeout /t 3 > nul
goto :menu

:get_params
cls
echo.
echo [96m--- 参数设置 ---[0m
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
set /p PASSWORD="请输入访问密码 ([93m留空表示不设密码[0m, 默认: %PASSWORD_DEFAULT%): "
if not defined PASSWORD set "PASSWORD=%PASSWORD_DEFAULT%"
echo.
goto :eof

:exit
exit /b
