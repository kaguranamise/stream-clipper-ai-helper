# -*- coding: utf-8 -*-
import subprocess
import shutil
from pathlib import Path
from typing import Union

class VideoEditor:
    """ffmpegを呼び出して動画の特定区間を切り出すクラス。
    
    システムに ffmpeg コマンドがインストールされていることを前提とし、
    subprocess を使用して正確な切り出し、または高速なコピー切り出しを実行します。
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        Args:
            ffmpeg_path (str): ffmpeg実行ファイルのパス。デフォルトは 'ffmpeg'。
        """
        self.ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()
        
    def _check_ffmpeg(self):
        """システム上に ffmpeg が存在するかチェックします。"""
        if not shutil.which(self.ffmpeg_path):
            raise RuntimeError(
                f"ffmpeg コマンドが見つかりませんでした。システムに ffmpeg がインストールされ、"
                f"環境変数 PATH に追加されているか確認してください。\n"
                f"実行パス: {self.ffmpeg_path}"
            )
            
    def cut_video(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        start_sec: float,
        duration_sec: float,
        accurate: bool = True
    ) -> bool:
        """動画の指定範囲を切り出して保存します。
        
        Args:
            input_path (Union[str, Path]): 入力動画ファイルのパス。
            output_path (Union[str, Path]): 切り出した動画の保存先パス。
            start_sec (float): 切り出し開始時間（秒）。
            duration_sec (float): 切り出し動画の長さ（秒）。
            accurate (bool): True の場合は再エンコードを行い、正確な秒数で切り出します。
                            False の場合はコーデックをコピー（-c copy）して高速に切り出しますが、
                            キーフレーム（I-frame）の位置によって開始時間が数秒ずれることがあります。
                            
        Returns:
            bool: 切り出しが成功した場合は True、失敗した場合は False。
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        # 保存先ディレクトリの自動作成
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 開始秒数がマイナスにならないように調整
        start_sec = max(0.0, start_sec)
        
        # ffmpeg コマンドの組み立て
        cmd = [self.ffmpeg_path, "-y"]  # 既存ファイルがある場合は上書き
        
        if accurate:
            # 正確な切り出しを行う場合
            # 入力ファイルを先に指定してデコードさせ、その後 -ss で指定した箇所から切り出して再エンコードします
            cmd.extend([
                "-ss", f"{start_sec:.3f}",
                "-i", str(input_path),
                "-t", f"{duration_sec:.3f}",
                "-c:v", "libx264",
                "-c:a", "aac",
                str(output_path)
            ])
        else:
            # 高速に切り出しを行う場合
            # -ss を入力ファイルの前に置くことで、キーフレームまで高速にシークし、
            # ストリームコピー（-c copy）で処理するため非常に高速ですが、ミリ秒単位の正確性はありません
            cmd.extend([
                "-ss", f"{start_sec:.3f}",
                "-i", str(input_path),
                "-t", f"{duration_sec:.3f}",
                "-c", "copy",
                str(output_path)
            ])
            
        try:
            # Windowsでの文字エンコーディングの混乱を防ぐために utf-8 を指定
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="ignore",
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"ffmpeg 処理中にエラーが発生しました。コマンド: {' '.join(cmd)}")
            print(f"エラーログ (stderr):\n{e.stderr}")
            return False
