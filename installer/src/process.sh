#!/bin/bash

# ログファイルを消去
echo "$(date) - /my_script.log をクリーンアップします..."
> /var/log/my_script.log
echo "$(date) - クリーンアップが完了しました。"

# ログファイルの設定
LOG_FILE="/var/log/my_script.log"
exec > >(tee -a $LOG_FILE) 2>&1

# 仮想環境を有効化
# shellcheck disable=SC1091
echo "$(date) - 仮想環境を有効化します。"
source /home/ec2-user/venv/bin/activate

# 環境変数を設定
# ※依頼書に記載された情報を使用
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_DEFAULT_REGION=ap-northeast-1

# スクリプトの開始時刻を記録
START_TIME=$(date +%s)

# スクリプトを実行
{
    # タイムゾーンを日本時間に設定
    export TZ=Asia/Tokyo

    echo "$(date) - スクリプトを開始します。"
    cd /home/ec2-user/site_monitor/installer/src || { echo "$(date) - ディレクトリの移動に失敗しました"; exit 1; }

    # メインスクリプト (main.py) を実行
    python main.py

    # 一時ディレクトリをクリーンアップ
    echo "$(date) - /tmp ディレクトリをクリーンアップします..."
    sudo rm -rf /tmp/.org.chromium.Chromium.*
    echo "$(date) - クリーンアップが完了しました。"

    # 仮想環境を無効化
    deactivate

    # 実行開始から1時間経過するまで待機
    echo "$(date) - インスタンスの停止まで1時間待機します..."
    while true; do
        CURRENT_TIME=$(date +%s)
        ELAPSED_TIME=$((CURRENT_TIME - START_TIME))

        echo "$(date) - 現在の経過時間: $ELAPSED_TIME 秒"

        # 実行開始から1時間経過した場合の処理
        if [ $ELAPSED_TIME -ge 3600 ]; then
            echo "$(date) - 1時間が経過しました。インスタンスを停止します..."
            if aws ec2 stop-instances --instance-ids i-07e411bca7ebac231; then
                echo "$(date) - インスタンスの停止に成功しました。"
            else
                echo "$(date) - インスタンスの停止に失敗しました！" >&2
            fi
            break
        fi

        # メインスクリプトが完了しているかチェック
        if ! pgrep -f "python main.py" > /dev/null; then
            echo "$(date) - メインスクリプトが完了しました。インスタンスを停止します..."
            if aws ec2 stop-instances --instance-ids i-07e411bca7ebac231; then
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
