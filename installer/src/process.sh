#!/bin/bash

# ログファイルの消去
echo "$(date) - Cleaning up /my_script.log..."
> /var/log/my_script.log
echo "$(date) - Cleanup completed."


# ログファイルの設定
LOG_FILE="/var/log/my_script.log"
exec > >(tee -a $LOG_FILE) 2>&1

# 仮想環境のアクティブ化
# shellcheck disable=SC1091
source /home/ec2-user/venv/bin/activate

# 環境変数の設定
#! 依頼書に記載
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_DEFAULT_REGION=ap-northeast-1

# スクリプトの開始
{
    # 日本時間に修正
    export TZ=Asia/Tokyo

    echo "$(date) - Starting script"
    cd /home/ec2-user/site_monitor/installer/src || { echo "$(date) - Failed to change directory"; exit 1; }
    # shellcheck disable=SC2094
    python main.py

    # /tmp ディレクトリのクリーンアップ
    echo "$(date) - Cleaning up /tmp directory..."
    sudo rm -rf /tmp/.org.chromium.Chromium.*
    echo "$(date) - Cleanup completed."

    # 仮想環境のディアクティベート
    deactivate

    # インスタンスを停止
    echo "$(date) - Stopping instance"
    sleep 10
    aws ec2 stop-instances --instance-ids i-07e411bca7ebac231

    echo "$(date) - Script finished"
}  | tee -a $LOG_FILE