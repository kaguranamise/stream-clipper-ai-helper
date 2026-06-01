# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Union, List, Dict, Any
from .reader import ChatLogReader
from .analyzer import ChatPeakAnalyzer
from .video import VideoEditor

class ClipPipeline:
    """データ入力、盛り上がり解析、動画切り出しの一連の工程（パイプライン）を管理するクラス。
    
    チャットログから盛り上がり箇所を検出し、それに基づき入力動画のハイライト区間を
    自動的に切り出して、指定されたディレクトリに保存します。
    """
    
    def __init__(
        self,
        window_sec: float = 30.0,
        threshold_multiplier: float = 2.0,
        duration_sec: float = 15.0,
        offset_sec: float = 10.0,
        accurate_cut: bool = True
    ):
        """
        Args:
            window_sec (float): チャット密度を計測する窓幅（秒）。
            threshold_multiplier (float): 盛り上がりと判定する平均チャット密度のしきい値倍率。
            duration_sec (float): 切り出す動画の長さ（秒）。
            offset_sec (float): 盛り上がりのピーク時点から何秒遡って切り出しを開始するか。
            accurate_cut (bool): True の場合は再エンコードによる正確な切り出し。False は高速なコピー。
        """
        self.window_sec = window_sec
        self.threshold_multiplier = threshold_multiplier
        self.duration_sec = duration_sec
        self.offset_sec = offset_sec
        self.accurate_cut = accurate_cut

    def run(
        self,
        video_path: Union[str, Path],
        log_path: Union[str, Path],
        output_dir: Union[str, Path]
    ) -> List[Path]:
        """パイプライン処理を実行します。
        
        Args:
            video_path (Union[str, Path]): 入力動画ファイルのパス。
            log_path (Union[str, Path]): チャットログファイルのパス。
            output_dir (Union[str, Path]): 切り出した動画を格納するディレクトリ。
            
        Returns:
            List[Path]: 生成された切り抜き動画ファイルのパスリスト。
        """
        video_path = Path(video_path)
        log_path = Path(log_path)
        output_dir = Path(output_dir)
        
        # 1. データの読み込み
        print(f"[1/3] チャットログを読み込み中: {log_path}")
        reader = ChatLogReader(log_path)
        df_chats = reader.read()
        print(f"      チャット件数: {len(df_chats)} 件")
        
        # 2. 盛り上がりの解析
        print(f"[2/3] チャットの盛り上がり（ピーク）を解析中 (窓幅: {self.window_sec}秒, しきい値倍率: {self.threshold_multiplier}倍)...")
        analyzer = ChatPeakAnalyzer(
            window_sec=self.window_sec,
            threshold_multiplier=self.threshold_multiplier
        )
        peaks = analyzer.analyze(df_chats)
        print(f"      見どころ検出数: {len(peaks)} 箇所")
        
        if not peaks:
            print("      見どころが検出されませんでした。しきい値（--threshold）を下げるか、データを確認してください。")
            return []
            
        # 3. 動画の切り出し
        print(f"[3/3] 動画の切り出しを開始します (出力先: {output_dir})...")
        editor = VideoEditor()
        output_files = []
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, peak in enumerate(peaks):
            peak_time = peak["timestamp_sec"]
            # 開始時間はピークから offset_sec 秒前。マイナス値にならないよう調整。
            start_time = max(0.0, peak_time - self.offset_sec)
            
            output_name = f"clip_{idx+1:03d}_at_{int(peak_time)}s.mp4"
            output_path = output_dir / output_name
            
            print(f"      [{idx+1}/{len(peaks)}] 切り出し中: {output_name} (開始: {start_time:.1f}秒, 長さ: {self.duration_sec}秒)")
            
            success = editor.cut_video(
                input_path=video_path,
                output_path=output_path,
                start_sec=start_time,
                duration_sec=self.duration_sec,
                accurate=self.accurate_cut
            )
            
            if success:
                output_files.append(output_path)
                print(f"      -> 成功: {output_path.name}")
            else:
                print(f"      -> 失敗: {output_name}")
                
        print(f"処理が終了しました。作成されたクリップ数: {len(output_files)}")
        return output_files
