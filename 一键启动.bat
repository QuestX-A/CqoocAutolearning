@echo off
chcp 936
REM 设置936编码防止某些中文路径导致批处理失效

setlocal enabledelayedexpansion
mode con cols=100 lines=30&color 0a&title 一键启动
echo.
echo [+] Quest X 向你问好
echo.
echo [+] 获得当前路径:%~dp0
echo.

:: 定义文件路径（基于脚本所在目录定位bin文件夹）
set "PY_SCRIPT=%~dp0bin\CqoocAutolearning-v3.2.py"
set "REQUIREMENTS=%~dp0bin\requirements.txt"

REM 脚本程序自检
if exist "%PY_SCRIPT%" (
	echo [+] 获得学习助手，路径：%PY_SCRIPT%
) else (
	echo [-] 注意,未发现学习助手启动脚本，请注意是否改名或移动...
	echo.
)

timeout /t 1 >nul	

echo.
echo ==============================================
echo [+] 正在尝试运行程序...
echo.
echo [+] 请不要关闭此窗口！
echo.
echo [+] 注释：如果网站已经登陆过，就不要在软件运行界面输入用户名和密码，网站会重复输入！
echo ==============================================

:: 尝试运行Python脚本
python "%PY_SCRIPT%"

:: 检查上一条命令的退出码（0=成功，非0=失败）
if %errorlevel% equ 0 (
    echo ==============================================
    echo [+]程序运行成功！
    echo ==============================================
    pause
    exit /b 0  :: 成功退出
) else (
    echo ==============================================
    echo [+]程序运行出错（可能缺少依赖），正在安装依赖...
	echo [+]请保持网络连接......
    echo ==============================================
    
if exist "%REQUIREMENTS%" (
	echo [+] 发现依赖清单，路径：%REQUIREMENTS%
) else (
	echo [-] 注意,未发现requirements.txt，请注意是否改名或移动...
	echo. 
) 
	
	timeout /t 1 >nul
	
    :: 配置镜像源并升级pip
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
    python.exe -m pip install --upgrade pip
    
    :: 安装依赖
    pip install -r "%REQUIREMENTS%"
    
	echo.
    echo ==============================================
    echo [+]依赖安装完成！请重新运行本脚本启动程序。
    echo ==============================================
    pause
    exit
    
)
