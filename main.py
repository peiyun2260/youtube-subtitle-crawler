import os
import json
import requests
from dotenv import load_dotenv
from yt_dlp import YoutubeDL
from datetime import datetime, timedelta
import html

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
CHANNEL_URL = os.getenv("CHANNEL_URL")
DATA_PATH = 'subtitles'
os.makedirs(DATA_PATH, exist_ok=True)

def send_discord_notification(message, file_path=None):
    if not DISCORD_WEBHOOK_URL:
        print("❌ Discord Webhook 未設定")
        return
    data = {"content": message}
    files = {'file': open(file_path, 'rb')} if file_path else None
    response = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)
    if response.status_code in (200, 204):
        print("✅ Discord 通知已發送")
    else:
        print(f"❌ Discord 發送失敗: {response.status_code} - {response.text}")

def is_within_days(upload_date_str, days=2):
    """
    upload_date_str 格式：'20240322'
    """
    if not upload_date_str:
        return False
    video_date = datetime.strptime(upload_date_str, '%Y%m%d')
    return datetime.now() - video_date <= timedelta(days=days)

def fetch_latest_video_ids_with_dates():
    ydl_opts = {
        'extract_flat': True,  # 快速拿影片 ID
        'skip_download': True,
        'quiet': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(CHANNEL_URL, download=False)

    video_list = []
    for entry in info['entries'][:3]:  # 只取最新3部影片
        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
        with YoutubeDL({'skip_download': True, 'quiet': True}) as ydl:
            video_info = ydl.extract_info(video_url, download=False)
            video_list.append({
                'id': video_info['id'],
                'upload_date': video_info.get('upload_date')
            })
    return video_list

def download_subtitle_and_srt(video_id):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'subtitlesformat': 'srt/vtt',
        'outtmpl': f'{DATA_PATH}/{video_id}.%(ext)s'
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.download([f'https://youtu.be/{video_id}'])
            # 嘗試找 srt，找不到就找 vtt
            if os.path.exists(f"{DATA_PATH}/{video_id}.en.srt"):
                return f"{DATA_PATH}/{video_id}.en.srt"
            elif os.path.exists(f"{DATA_PATH}/{video_id}.en.vtt"):
                return f"{DATA_PATH}/{video_id}.en.vtt"
            else:
                print(f"⚠️ 找不到字幕檔案 {video_id}")
                return None
    except Exception as e:
        print(f"❌ 字幕下載失敗 {video_id}: {e}")
        return None


def clean_and_convert_to_txt(sub_file):
    txt_file = sub_file.rsplit('.', 1)[0] + '.txt'
    with open(sub_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 轉換 HTML entities
    cleaned_content = html.unescape(content)

    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    return txt_file


def safe_load_downloaded(filepath):
    if not os.path.exists(filepath):
        return set()
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return set(data)
    except (json.JSONDecodeError, ValueError):
        print("⚠️ 下載紀錄檔損毀或為空，重置為空集合")
        return set()

def main():
    downloaded_file = 'downloaded.json'
    downloaded = safe_load_downloaded(downloaded_file)

    videos = fetch_latest_video_ids_with_dates()

    new_videos_recent = [
        video['id'] for video in videos
        if is_within_days(video.get('upload_date'), days=2) and video['id'] not in downloaded
    ]


    if not new_videos_recent:
        print("🟢 最近兩天沒有新影片")
        return

    for video_id in new_videos_recent:
        srt_file = download_subtitle_and_srt(video_id)
        if srt_file:
            txt_file = clean_and_convert_to_txt(srt_file)  # ✅ 清理 &nbsp; 並轉 txt
            downloaded.add(video_id)
            send_discord_notification(f"🎉 新字幕下載成功！\nhttps://youtu.be/{video_id}", txt_file)

    print(f"✅ 寫入 downloaded.json: {downloaded}")
    with open(downloaded_file, 'w') as f:
        json.dump(list(downloaded), f, indent=2)

if __name__ == '__main__':
    main()
