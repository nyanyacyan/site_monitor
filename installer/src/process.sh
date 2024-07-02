#!/bin/bash

# ログファイルの設定
LOG_FILE="/var/log/my_script.log"
exec > >(tee -a $LOG_FILE) 2>&1

# /tmp ディレクトリのクリーンアップ
echo "$(date) - Cleaning up /tmp directory..."
find /tmp -type f -atime +10 -exec rm -f {} \;
find /tmp -type d -empty -atime +10 -exec rm -rf {} \;
echo "$(date) - Cleanup completed."

# スクリプトの開始
echo "$(date) - Starting script"
cd /home/ec2-user/site_monitor/installer/src || { echo "$(date) - Failed to change directory"; exit 1; }
python main.py 2>&1 | tee -a /var/log/my_script.log

# インスタンスを停止
echo "$(date) - Stopping instance"
sleep 10
aws ec2 stop-instances --instance-ids i-0a1629d8026f15e8c

echo "$(date) - Script finished"