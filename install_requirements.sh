#!/bin/bash

# 定义日志文件
LOGFILE="install_requirements.log"

# 记录当前日期和时间到日志文件
echo "[$(date)] 开始执行脚本..." >> "$LOGFILE"

# 检查是否提供了requirements.txt文件的URL
if [ "$#" -ne 1 ]; then
  echo "用法: $0 <requirements.txt 文件的URL>" | tee -a "$LOGFILE"
  exit 1
fi

REQUIREMENTS_URL=$1
REQUIREMENTS_FILE="requirements.txt"

# 下载requirements.txt文件并显示进度条
echo "下载 $REQUIREMENTS_URL 到 $REQUIREMENTS_FILE ..." | tee -a "$LOGFILE"
curl -o "$REQUIREMENTS_FILE" --progress-bar "$REQUIREMENTS_URL" >> "$LOGFILE" 2>&1

# 检查是否下载成功
if [ ! -f "$REQUIREMENTS_FILE" ]; then
  echo "下载失败。请检查URL是否正确。" | tee -a "$LOGFILE"
  exit 1
fi

echo "$REQUIREMENTS_FILE 下载成功。" | tee -a "$LOGFILE"

# 检测Python环境
if command -v python3 &> /dev/null; then
  echo "Python 3 已安装。" | tee -a "$LOGFILE"
  python3 --version | tee -a "$LOGFILE"
else
  echo "Python 3 未安装。" | tee -a "$LOGFILE"
  read -p "是否希望安装 Python 3？（y/n）: " install_python

  if [ "$install_python" = "y" ]; then
    echo "开始安装 Python 3..." | tee -a "$LOGFILE"
    
    # 检测操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
      if [ -x "$(command -v apt-get)" ]; then
        sudo apt-get update >> "$LOGFILE" 2>&1
        sudo apt-get install -y python3 python3-pip >> "$LOGFILE" 2>&1
      elif [ -x "$(command -v yum)" ]; then
        sudo yum install -y python3 python3-pip >> "$LOGFILE" 2>&1
      elif [ -x "$(command -v dnf)" ]; then
        sudo dnf install -y python3 python3-pip >> "$LOGFILE" 2>&1
      elif [ -x "$(command -v pacman)" ]; then
        sudo pacman -Syu --noconfirm python python-pip >> "$LOGFILE" 2>&1
      else
        echo "无法识别的包管理器，请手动安装 Python 3 和 pip3。" | tee -a "$LOGFILE"
        exit 1
      fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
      if command -v brew &> /dev/null; then
        brew install python >> "$LOGFILE" 2>&1
      else
        echo "Homebrew 未安装，请先安装 Homebrew 或手动安装 Python 3。" | tee -a "$LOGFILE"
        exit 1
      fi
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
      if command -v winget &> /dev/null; then
        winget install Python.Python.3 >> "$LOGFILE" 2>&1
      elif command -v choco &> /dev/null; then
        choco install python >> "$LOGFILE" 2>&1
      else
        echo "无法识别的包管理器，请手动安装 Python 3。" | tee -a "$LOGFILE"
        exit 1
      fi
    else
      echo "不支持的操作系统，请手动安装 Python 3 和 pip3。" | tee -a "$LOGFILE"
      exit 1
    fi
  else
    echo "请手动安装 Python 3 和 pip3。" | tee -a "$LOGFILE"
    exit 1
  fi
fi

# 检测pip是否可用
if command -v pip3 &> /dev/null; then
  echo "pip3 已安装。" | tee -a "$LOGFILE"
  pip3 --version | tee -a "$LOGFILE"
else
  echo "pip3 未安装。" | tee -a "$LOGFILE"
  read -p "是否希望安装 pip3？（y/n）: " install_pip

  if [ "$install_pip" = "y" ]; then
    echo "开始安装 pip3..." | tee -a "$LOGFILE"

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
      if [ -x "$(command -v apt-get)" ]; then
        sudo apt-get install -y python3-pip >> "$LOGFILE" 2>&1
      elif [ -x "$(command -v yum)" ]; then
        sudo yum install -y python3-pip >> "$LOGFILE" 2>&1
      elif [ -x "$(command -v dnf)" ]; then
        sudo dnf install -y python3-pip >> "$LOGFILE" 2>&1
      elif [ -x "$(command -v pacman)" ]; then
        sudo pacman -Syu --noconfirm python-pip >> "$LOGFILE" 2>&1
      else
        echo "无法识别的包管理器，请手动安装 pip3。" | tee -a "$LOGFILE"
        exit 1
      fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
      if command -v brew &> /dev/null; then
        brew install python >> "$LOGFILE" 2>&1
      else
        echo "Homebrew 未安装，请先安装 Homebrew 或手动安装 pip3。" | tee -a "$LOGFILE"
        exit 1
      fi
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
      echo "pip3 通常随 Python 一起安装。如果没有，请手动安装。" | tee -a "$LOGFILE"
      exit 1
    else
      echo "不支持的操作系统，请手动安装 pip3。" | tee -a "$LOGFILE"
      exit 1
    fi
  else
    echo "请手动安装 pip3。" | tee -a "$LOGFILE"
    exit 1
  fi
fi

# 使用pip安装requirements.txt中的依赖，并使用国内镜像源作为备用
echo "正在安装requirements.txt中的依赖..." | tee -a "$LOGFILE"
pip3 install -r "$REQUIREMENTS_FILE" >> "$LOGFILE" 2>&1

# 如果安装失败，使用国内镜像源重试
if [ $? -ne 0 ]; then
  echo "依赖项安装失败，切换到国内镜像源重试..." | tee -a "$LOGFILE"
  pip3 install -r "$REQUIREMENTS_FILE" -i https://pypi.tuna.tsinghua.edu.cn/simple >> "$LOGFILE" 2>&1
fi

# 检查pip安装的结果
if [ $? -eq 0 ]; then
  echo "依赖项安装成功。" | tee -a "$LOGFILE"
else
  echo "依赖项安装失败。" | tee -a "$LOGFILE"
  exit 1
fi

# 结束日志记录
echo "[$(date)] 脚本执行完毕。" >> "$LOGFILE"
