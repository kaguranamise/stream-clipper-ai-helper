# stream-clipper

[English](#english) | [日本語](#日本語-japanese)

---

## English

A Python-based CLI tool designed to automatically detect chat activity peaks (and future audio volume peaks) from streaming video archives and extract clip highlights.

### Features & Architecture

To support future enhancements (such as AI-driven video metadata/audio analysis and advanced filtering), this project is built on a clean pipeline structure. Each phase is separated into distinct, modular components.

```
[Chat Log/Video Archive] 
           │
           ▼
 1. Data Input (reader.py)  ── Normalizes and parses CSV/JSON chat logs.
           │
           ▼
 2. Peak Analysis (analyzer.py) ── Identifies peak highlight moments using a sliding window.
           │
           ▼
 3. Video Editing (video.py) ── Spawns ffmpeg to clip the video precisely.
```

### Requirements

- Python 3.8+
- **ffmpeg** command-line tool
  - `ffmpeg` must be installed on your system and added to your system's `PATH` environment variable for video clipping functionality.

### Installation

Run the following command in the root directory of this repository to install the package in development mode:

```bash
pip install -e .
```

This will install the necessary dependencies (`click`, `pandas`, `numpy`) and register the `stream-clipper` command globally on your system/virtual environment.

### Usage

The basic command structure is as follows:

```bash
stream-clipper clip [VIDEO_PATH] [LOG_PATH] [OPTIONS]
```

#### Examples

```bash
# Basic run with default parameters (outputs clips to ./output)
stream-clipper clip stream_archive.mp4 chat_log.csv

# Run with custom parameters: 10s window, 3x threshold, offset 5s before the peak, clipping for 10s
stream-clipper clip stream_archive.mp4 chat_log.json --window 10 --threshold 3.0 --offset 5 --duration 10 --output-dir custom_clips/
```

#### Command Options

| Option | Default Value | Description |
| :--- | :--- | :--- |
| `--window` | `30.0` | Time window (seconds) to measure chat density. |
| `--threshold` | `2.0` | The multiplier of the overall mean chat density to detect a peak. |
| `--duration` | `15.0` | The duration of the output clip (seconds). |
| `--offset` | `10.0` | How many seconds before the peak timestamp the clip should start. |
| `--output-dir` | `output` | Directory where the generated video clips will be saved. |
| `--fast` | None (Flag) | Enables fast stream-copy clipping (`-c copy`). This matches keyframes and is extremely fast, but starting/ending positions may be slightly imprecise. |

### Development & Testing

#### Generating Mock Assets

Before running tests or checking CLI functionality, generate a 60-second dummy video (with color bars and tone audio) and mock chat logs (with simulated spikes between 30 and 45 seconds):

```bash
python tests/generate_test_assets.py
```

#### Running Unit Tests

Run the following command to execute the test suite:

```bash
python -m unittest tests/test_pipeline.py
```

---

## 日本語-japanese

配信アーカイブ動画から、チャットの盛り上がり（および将来的な音量ピークなど）を検知して自動で切り抜き動画の素材を抽出するPython製のCLIツールです。

### 特徴とアーキテクチャ

将来的な機能拡張（AIによる動画メタデータ/音声の認識、高度なフィルタリングなど）を見据え、クリーンなパイプライン構造を採用しています。それぞれのフェーズが独立したモジュールとして設計されています。

```
[チャットログ/動画] 
       │
       ▼
 1. データ入力 (reader.py)  ── CSV/JSONチャットログを正規化して読み込み
       │
       ▼
 2. 盛り上がり解析 (analyzer.py) ── スライディングウィンドウでピークを検出
       │
       ▼
 3. 動画編集 (video.py)     ── ffmpegを呼び出して正確に切り出し
```

### 必要条件

- Python 3.8 以上
- **ffmpeg** コマンド
  - 動画の切り出しにシステムへインストールされた `ffmpeg` を使用します。実行環境の環境変数 `PATH` に `ffmpeg` が含まれている必要があります。

### インストール方法

本リポジトリのルートディレクトリで以下のコマンドを実行し、パッケージを開発モードでインストールします。

```bash
pip install -e .
```

これにより、依存パッケージ（`click`, `pandas`, `numpy`）がインストールされ、`stream-clipper` コマンドがシステム全体（または仮想環境）から直接利用可能になります。

### 使い方

基本のコマンド構造は以下の通りです。

```bash
stream-clipper clip [動画パス] [ログパス] [オプション]
```

#### 使用例

```bash
# 基本的な実行 (デフォルト設定で出力先は ./output)
stream-clipper clip stream_archive.mp4 chat_log.csv

# パラメータを指定して実行 (窓幅10秒、しきい値3倍、ピークから5秒前遡って10秒切り出し)
stream-clipper clip stream_archive.mp4 chat_log.json --window 10 --threshold 3.0 --offset 5 --duration 10 --output-dir custom_clips/
```

#### 主要オプション

| オプション | デフォルト値 | 説明 |
| :--- | :--- | :--- |
| `--window` | `30.0` | チャットの盛り上がり（密度）を計算する時間幅（秒） |
| `--threshold` | `2.0` | 全体平均チャット密度の何倍を超えたら盛り上がり（ピーク）と判定するかのしきい値 |
| `--duration` | `15.0` | 切り出し動画の秒数 |
| `--offset` | `10.0` | 検出したピークのタイムスタンプから何秒遡って切り出しを開始するか |
| `--output-dir` | `output` | 切り出した動画ファイルの保存先ディレクトリ |
| `--fast` | なし (フラグ) | キーフレームに合わせて高速な切り出しを行う（ストリームコピー）。正確な開始秒数での切り出しは行いませんが、非常に高速です。 |

### 開発とテスト

#### テスト用アセットの生成

テストを実行する前に、以下のスクリプトを走らせることで、自動的にテスト用の擬似チャットログ（CSV / JSON）とダミー動画（60秒のカラーバーとオーディオ）を生成します。

```bash
python tests/generate_test_assets.py
```

#### ユニットテストの実行

作成したモジュールの正確性を検証するためのユニットテストを以下で実行できます。

```bash
python -m unittest tests/test_pipeline.py
```
