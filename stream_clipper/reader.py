# -*- coding: utf-8 -*-
import csv
import json
from pathlib import Path
from typing import List, Dict, Union
import pandas as pd

class ChatLogReader:
    """チャットログファイルを読み込み、DataFrameに変換するクラス。
    
    CSV または JSON 形式のログファイルを自動判別してパースし、
    タイムスタンプを秒数（float）に統一したデータ構造を提供します。
    """
    
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        
    def read(self) -> pd.DataFrame:
        """ログファイルを読み込んで pandas.DataFrame を返します。
        
        期待するカラム:
        - timestamp: 動画開始からの経過時間（秒数、または HH:MM:SS / MM:SS 形式の文字列）
        - message: チャットの本文
        
        返り値の DataFrame には以下の列が含まれます:
        - timestamp: 元のタイムスタンプ値
        - message: チャット本文
        - timestamp_sec: 解析用に秒数に変換した数値 (float)
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"チャットログファイルが見つかりません: {self.file_path}")
            
        suffix = self.file_path.suffix.lower()
        if suffix == '.csv':
            df = pd.read_csv(self.file_path)
        elif suffix == '.json':
            # pandasがタイムスタンプ文字列を日付型に自動変換しないように convert_dates=False を指定
            df = pd.read_json(self.file_path, convert_dates=False)
        else:
            raise ValueError(f"未対応のファイル形式です: {suffix} (CSV または JSON のみサポートしています)")
            
        # 必須カラムのチェック
        required_cols = {'timestamp', 'message'}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"チャットログには {required_cols} カラムが必要です。取得したカラム: {list(df.columns)}")
            
        # タイムスタンプを秒数（float）に正規化
        df['timestamp_sec'] = df['timestamp'].apply(self._parse_timestamp)
        return df

    def _parse_timestamp(self, ts: Union[int, float, str]) -> float:
        """様々な形式のタイムスタンプを秒数（float）に変換します。
        
        例:
        - 83 -> 83.0
        - "83.5" -> 83.5
        - "00:01:23" -> 83.0
        - "01:23" -> 83.0
        """
        if isinstance(ts, (int, float)):
            return float(ts)
            
        ts_str = str(ts).strip()
        
        # 単純な数値文字列の場合の変換
        try:
            return float(ts_str)
        except ValueError:
            pass
            
        # コロン区切り (HH:MM:SS または MM:SS) の場合のパース
        parts = ts_str.split(':')
        if len(parts) == 3:
            h, m, s = parts
            return float(h) * 3600 + float(m) * 60 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return float(m) * 60 + float(s)
            
        raise ValueError(f"無効なタイムスタンプフォーマットです: {ts}")
