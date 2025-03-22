## YouTube Subtitle Crawler - 自動抓取 YouTube 頻道字幕並發送到 Discord

## 專案功能：

- 自動排程每天抓取指定 YouTube 頻道最新 2 天內的影片
- 下載英文自動字幕（.srt / .vtt）
- 自動清理 HTML 符號
- 轉成 .txt 檔，直接發送到 Discord 頻道（手機可直接觀看）
- 支援排程 log 紀錄

## 目錄結構：

- main.py 主程式
- Dockerfile Docker 建構檔
- requirements.txt 乾淨版本需求套件
- subtitles/ 存放下載的字幕
- downloaded.json 已下載過的影片紀錄
- .env Discord Webhook 設定
- cron.log 排程執行紀錄

## .env 範例：

DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_here
CHANNEL_URL=https://www.youtube.com/@youtubeChannel/videos

## 常用指令：

make build # 建立 docker image
make run # 手動執行一次
make cron # 設定每天晚上 10 點自動執行
make show-cron # 查看目前排程
make remove-cron# 移除排程
make prune # 清理無用 docker image
make log-clean # 清空 cron.log

## 注意事項：

- cron.log 會累積，可用 make log-clean 清空
- downloaded.json 記錄已處理過的影片，避免重複下載

## 套件需求（requirements.txt）：

python-dotenv
requests
yt-dlp
