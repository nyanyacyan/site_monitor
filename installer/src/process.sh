#!/bin/bash

# ログファイルの設定
LOG_FILE="/var/log/my_script.log"
exec > >(tee -a $LOG_FILE) 2>&1

# 環境変数の出力
env > /home/ec2-user/script_env.txt

echo "$(date) - Checking Python version..."
PYTHON_VERSION=$(/usr/bin/python3.8 --version 2>&1)
if [[ $PYTHON_VERSION != "Python 3.8.10" ]]; then
    echo "$(date) - Python 3.8.10 not found, installing..."
    sudo yum -y update
    sudo yum -y install gcc openssl-devel bzip2-devel libffi-devel
    cd /usr/src
    sudo wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tgz
    sudo tar xzf Python-3.8.10.tgz
    cd Python-3.8.10
    sudo ./configure --enable-optimizations
    sudo make altinstall
    echo "$(date) - Python 3.8.10 installed"
else
    echo "$(date) - Python 3.8.10 already installed"
fi

# パッケージのインストール
echo "$(date) - Installing required Python libraries"
sudo /usr/local/bin/python3.8 -m pip install -r /home/ec2-user/site_monitor/bin/requirements.txt

# スクリプトの開始
echo "$(date) - Starting script"
cd /home/ec2-user/site_monitor/installer/src || { echo "$(date) - Failed to change directory"; exit 1; }


/usr/bin/python3.8 main.py 2>&1 | tee -a /var/log/my_script.log

# /tmp ディレクトリのクリーンアップ
echo "$(date) - Cleaning up /tmp directory..."
find /tmp -type f -atime +10 -exec rm -f {} \;
find /tmp -type d -empty -atime +10 -exec rm -rf {} \;
echo "$(date) - Cleanup completed."

# インスタンスを停止
echo "$(date) - Stopping instance"
sleep 10
aws ec2 stop-instances --instance-ids i-0a1629d8026f15e8c

echo "$(date) - Script finished"