# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from typing import List, Dict, Any

class ChatPeakAnalyzer:
    """チャットログの密度から盛り上がりのピークを検出する解析クラス。
    
    指定された窓幅（window_sec）におけるチャットの出現頻度を計算し、
    全体の平均頻度に対してしきい値（threshold_multiplier）を超える区間の
    最大値（ローカルピーク）を「見どころ」として検出します。
    """
    
    def __init__(self, window_sec: float = 30.0, threshold_multiplier: float = 2.0):
        """
        Args:
            window_sec (float): チャット密度を計測する時間幅（秒）。
            threshold_multiplier (float): 盛り上がりと判定するしきい値の倍率（平均値に対する比率）。
        """
        self.window_sec = window_sec
        self.threshold_multiplier = threshold_multiplier

    def analyze(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """チャットの時系列データから盛り上がりのピークとなるタイムスタンプを検出します。
        
        Args:
            df (pd.DataFrame): 'timestamp_sec' カラムを含むチャットログのDataFrame。
            
        Returns:
            List[Dict[str, Any]]: 検出されたピークのリスト。
                各要素は以下の形式の辞書です:
                {
                    "timestamp_sec": float (ピーク時のタイムスタンプ秒数),
                    "chat_count": int (窓幅内での合計チャット数),
                    "density": float (1秒あたりの平均チャット数)
                }
        """
        if df.empty:
            return []
            
        # タイムスタンプ順に並び替え
        df_sorted = df.sort_values('timestamp_sec')
        
        min_time = df_sorted['timestamp_sec'].min()
        max_time = df_sorted['timestamp_sec'].max()
        
        # 時系列を1秒ごとに離散化してチャット数を集計
        # 動画時間に応じた配列を初期化
        duration = int(np.ceil(max_time - min_time)) + 1
        time_series = np.zeros(duration)
        
        for ts in df_sorted['timestamp_sec']:
            idx = int(np.floor(ts - min_time))
            if 0 <= idx < duration:
                time_series[idx] += 1
                
        # 移動平均（ローリング合計）により、窓幅内のチャット合計数を計算
        window = int(self.window_sec)
        if window <= 0:
            window = 1
            
        ts_series = pd.Series(time_series)
        # center=True にすることで、現在時刻を中心に前後 window/2 秒の合計とする
        rolling_sum = ts_series.rolling(window=window, min_periods=1, center=True).sum()
        
        # 基準となる平均チャット密度と検出用のしきい値を設定
        mean_density = rolling_sum.mean()
        threshold = mean_density * self.threshold_multiplier
        
        peaks = []
        is_peak = False
        current_peak_val = -1.0
        current_peak_idx = -1
        
        # 簡易的なピークファインダー:
        # しきい値を超えている区間の中で、極大値（最も値が大きい点）をピークとして採用する
        for idx, val in enumerate(rolling_sum):
            if val >= threshold:
                if not is_peak:
                    is_peak = True
                    current_peak_val = val
                    current_peak_idx = idx
                else:
                    if val > current_peak_val:
                        current_peak_val = val
                        current_peak_idx = idx
            else:
                if is_peak:
                    peaks.append({
                        "timestamp_sec": float(min_time + current_peak_idx),
                        "chat_count": int(current_peak_val),
                        "density": float(current_peak_val / self.window_sec)
                    })
                    is_peak = False
                    
        # ログ末尾でピークが継続していた場合の処理
        if is_peak:
            peaks.append({
                "timestamp_sec": float(min_time + current_peak_idx),
                "chat_count": int(current_peak_val),
                "density": float(current_peak_val / self.window_sec)
            })
            
        return peaks
