# -*- coding: utf-8 -*-
import json
import csv
import subprocess
import shutil
from pathlib import Path

def generate_assets():
    """テスト用のダミー動画および擬似チャットログを生成します。
    
    チャットログは 60 秒間のうち、30秒〜45秒付近にチャットが集中するよう構成されています。
    動画は ffmpeg コマンドを用いて 60秒のダミー動画を生成します。
    """
    test_dir = Path(__file__).parent
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 擬似チャットログの生成 (CSV)
    csv_path = test_dir / "test_chat.csv"
    print(f"CSV チャットログを作成中: {csv_path}")
    
    chats = []
    # 通常時: 5秒に1件
    # 盛り上がり時 (30〜45秒): 1秒に4件
    for sec in range(0, 60):
        if sec < 30 or sec > 45:
            if sec % 5 == 0:
                chats.append((f"00:00:{sec:02d}", f"user_{sec}", "こんにちは！"))
        else:
            for i in range(4):
                chats.append((f"00:00:{sec:02d}", f"user_{sec}_{i}", f"うおおおお wwww {i}"))
                
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "username", "message"])
        writer.writerows(chats)
    print("CSV チャットログ作成完了")
        
    # 2. 擬似チャットログの生成 (JSON)
    json_path = test_dir / "test_chat.json"
    print(f"JSON チャットログを作成中: {json_path}")
    json_chats = [{"timestamp": item[0], "username": item[1], "message": item[2]} for item in chats]
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_chats, f, indent=2, ensure_ascii=False)
    print("JSON チャットログ作成完了")
        
    # 3. ダミー動画の生成 (ffmpeg がシステムにインストールされている場合のみ)
    video_path = test_dir / "test_video.mp4"
    if shutil.which("ffmpeg"):
        print(f"ffmpegを使用してダミー動画を生成中: {video_path}")
        # 60秒のテスト用カラーバー映像と無音オーディオを合成
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "testsrc=duration=60:size=640x360:rate=30",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=60",
            "-c:v", "libx264", "-c:a", "aac",
            str(video_path)
        ]
        try:
            # 進捗表示が多くなるため、出力を抑える
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("ダミー動画生成完了")
        except subprocess.CalledProcessError as e:
            print(f"ダミー動画生成中にエラーが発生しました: {e}")
            print(f"stderr:\n{e.stderr.decode('utf-8', errors='ignore')}")
    else:
        print("警告: ffmpeg コマンドが見つからないため、ダミー動画の生成をスキップします。")

if __name__ == "__main__":
    generate_assets()
