# -*- coding: utf-8 -*-
import sys
import shutil
from pathlib import Path
import unittest

# プロジェクトルートを sys.path に追加して stream_clipper パッケージをインポート可能にする
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from stream_clipper.reader import ChatLogReader
from stream_clipper.analyzer import ChatPeakAnalyzer
from stream_clipper.pipeline import ClipPipeline
from tests.generate_test_assets import generate_assets

class TestStreamClipper(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """テスト前にダミーアセットを一回だけ生成します。"""
        generate_assets()
        cls.test_dir = Path(__file__).parent
        cls.csv_path = cls.test_dir / "test_chat.csv"
        cls.json_path = cls.test_dir / "test_chat.json"
        cls.video_path = cls.test_dir / "test_video.mp4"
        cls.output_dir = cls.test_dir / "output_test"
        
    def test_reader_csv(self):
        """CSV形式のチャットログの読み込みとタイムスタンプの秒数変換をテストします。"""
        reader = ChatLogReader(self.csv_path)
        df = reader.read()
        self.assertFalse(df.empty, "DataFrameが空です")
        self.assertIn("timestamp_sec", df.columns, "timestamp_sec 列が存在しません")
        # 30秒〜45秒のデータが含まれているか
        self.assertTrue((df["timestamp_sec"] >= 30).any(), "30秒以降のデータが含まれていません")
        
    def test_reader_json(self):
        """JSON形式のチャットログの読み込みとタイムスタンプの秒数変換をテストします。"""
        reader = ChatLogReader(self.json_path)
        df = reader.read()
        self.assertFalse(df.empty, "DataFrameが空です")
        self.assertIn("timestamp_sec", df.columns, "timestamp_sec 列が存在しません")
        
    def test_analyzer(self):
        """チャットログ密度からのピーク検出ロジックをテストします。"""
        reader = ChatLogReader(self.csv_path)
        df = reader.read()
        
        # 窓幅 10秒、しきい値倍率 2.0 でテスト
        analyzer = ChatPeakAnalyzer(window_sec=10.0, threshold_multiplier=2.0)
        peaks = analyzer.analyze(df)
        
        self.assertGreater(len(peaks), 0, "ピークが1つも検出されませんでした")
        
        # 30秒から45秒の間にピークが検出されていることを確認
        peak_times = [p["timestamp_sec"] for p in peaks]
        has_correct_peak = any(30 <= pt <= 48 for pt in peak_times)
        self.assertTrue(has_correct_peak, f"期待する時間帯（30〜48秒）にピークがありません。検出されたピーク: {peak_times}")

    def test_pipeline(self):
        """入力 -> 解析 -> 切り出しのパイプライン全体の動作をテストします。"""
        if not self.video_path.exists():
            self.skipTest("ffmpeg がインストールされていないため、ダミー動画が存在せず、動画切り出しテストをスキップします")
            
        # パイプラインのパラメータ設定
        pipeline = ClipPipeline(
            window_sec=10.0,
            threshold_multiplier=2.0,
            duration_sec=5.0,  # 5秒間の動画を切り出す
            offset_sec=2.0,    # ピークの2秒前から切り出し
            accurate_cut=True
        )
        
        # 出力ディレクトリが存在する場合は一旦クリーンアップ
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            
        output_files = pipeline.run(
            video_path=self.video_path,
            log_path=self.csv_path,
            output_dir=self.output_dir
        )
        
        self.assertGreater(len(output_files), 0, "切り抜き動画が生成されませんでした")
        for path in output_files:
            self.assertTrue(path.exists(), f"生成されたファイルが存在しません: {path}")
            self.assertGreater(path.stat().st_size, 0, f"生成されたファイルが空です: {path}")

if __name__ == "__main__":
    unittest.main()
