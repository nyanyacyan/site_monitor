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

    # ログファイルの追加クリーンアップ
    echo "$(date) - Additional log cleanup starting..."
    sudo rm -rf /var/log/awslogs.log*
    sudo rm -rf /var/log/messages*
    sudo rm -rf /home/ec2-user/site_monitor/installer/src/method/logs/*
    echo "$(date) - Additional log cleanup completed."

    # /tmp ディレクトリのクリーンアップ
    echo "$(date) - Cleaning up /tmp directory..."
    sudo rm -rf /tmp/.org.chromium.Chromium.*
    echo "$(date) - /tmp cleanup completed."

    # 仮想環境のディアクティベート
    deactivate

    # インスタンスの停止ロジック
    echo "$(date) - インスタンスの停止まで1時間待機します..."
    while true; do
        CURRENT_TIME=$(date +%s)
        ELAPSED_TIME=$((CURRENT_TIME - START_TIME))

        echo "$(date) - 現在の経過時間: $ELAPSED_TIME 秒"

        # 1時間が経過した場合の処理
        if [ $ELAPSED_TIME -ge 3600 ]; then
            echo "$(date) - 1時間が経過しました。インスタンスを停止します..."
            timeout 60 aws ec2 stop-instances --instance-ids i-07e411bca7ebac231
            if [ $? -eq 0 ]; then
                echo "$(date) - インスタンスの停止に成功しました。"
            else
                echo "$(date) - インスタンスの停止に失敗しました！" >&2
            fi
            break
        fi

        # メインスクリプトが完了しているかチェック
        if ! ps -p $MAIN_PID > /dev/null; then
            echo "$(date) - メインスクリプトが完了しました。インスタンスを停止します..."
            timeout 60 aws ec2 stop-instances --instance-ids i-07e411bca7ebac231
            if [ $? -eq 0 ]; then
                echo "$(date) - インスタンスの停止に成功しました。"
            else
                echo "$(date) - インスタンスの停止に失敗しました！" >&2
            fi
            break
        fi

        # 10秒ごとに状態をチェック
        sleep 10
    done

    echo "$(date) - スクリプトが終了しました。"
} | tee -a $LOG_FILE
