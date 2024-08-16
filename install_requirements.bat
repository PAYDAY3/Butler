@echo off
REM 定义日志文件
set LOGFILE=install_requirements.log

REM 记录当前日期和时间到日志文件
echo [%date% %time%] 开始执行脚本... >> %LOGFILE%

REM 检查是否提供了requirements.txt文件的URL
if "%~1"=="" (
    echo 用法: %~nx0 <requirements.txt 文件的URL> | tee -a %LOGFILE%
    exit /b 1
)

set REQUIREMENTS_URL=%~1
set REQUIREMENTS_FILE=requirements.txt

REM 下载requirements.txt文件并显示进度条
echo 正在下载 %REQUIREMENTS_URL% 到 %REQUIREMENTS_FILE%... | tee -a %LOGFILE%
powershell -Command "Invoke-WebRequest -Uri %REQUIREMENTS_URL% -OutFile %REQUIREMENTS_FILE%" >> %LOGFILE% 2>&1

REM 检查是否下载成功
if not exist %REQUIREMENTS_FILE% (
    echo 下载失败。请检查URL是否正确。 | tee -a %LOGFILE%
    exit /b 1
)

echo %REQUIREMENTS_FILE% 下载成功。 | tee -a %LOGFILE%

REM 检测是否安装了 Python 3
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 3 未安装。 | tee -a %LOGFILE%
    set /p install_python=是否希望安装 Python 3？（y/n）: 
    if /i "%install_python%"=="y" (
        echo 请手动安装 Python 3 和 pip3，然后重试。 | tee -a %LOGFILE%
        exit /b 1
    ) else (
        echo 请手动安装 Python 3 和 pip3。 | tee -a %LOGFILE%
        exit /b 1
    )
) else (
    echo Python 3 已安装。 | tee -a %LOGFILE%
    python --version | tee -a %LOGFILE%
)

REM 检测是否安装了 pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip 未安装。 | tee -a %LOGFILE%
    set /p install_pip=是否希望安装 pip？（y/n）: 
    if /i "%install_pip%"=="y" (
        echo 请手动安装 pip3，然后重试。 | tee -a %LOGFILE%
        exit /b 1
    ) else (
        echo 请手动安装 pip3。 | tee -a %LOGFILE%
        exit /b 1
    )
) else (
    echo pip 已安装。 | tee -a %LOGFILE%
    pip --version | tee -a %LOGFILE%
)

REM 使用pip安装requirements.txt中的依赖，并使用国内镜像源作为备用
echo 正在安装requirements.txt中的依赖... | tee -a %LOGFILE%
pip install -r %REQUIREMENTS_FILE% >> %LOGFILE% 2>&1

REM 如果安装失败，使用国内镜像源重试
if %errorlevel% neq 0 (
    echo 依赖项安装失败，切换到国内镜像源重试... | tee -a %LOGFILE%
    pip install -r %REQUIREMENTS_FILE% -i https://pypi.tuna.tsinghua.edu.cn/simple >> %LOGFILE% 2>&1
)

REM 检查pip安装的结果
if %errorlevel% neq 0 (
    echo 依赖项安装失败。 | tee -a %LOGFILE%
    exit /b 1
) else (
    echo 依赖项安装成功。 | tee -a %LOGFILE%
)

REM 结束日志记录
echo [%date% %time%] 脚本执行完毕。 >> %LOGFILE%
