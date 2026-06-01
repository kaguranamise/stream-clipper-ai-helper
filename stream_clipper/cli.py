# -*- coding: utf-8 -*-
import click
from pathlib import Path
from .pipeline import ClipPipeline

@click.group()
def main():
    """配信アーカイブからチャットの盛り上がりを検知し、自動で切り抜き動画を抽出するツール"""
    pass

@main.command()
@click.argument('video_path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('log_path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--window', default=30.0, type=float, help='チャットの盛り上がりを計算する時間幅（秒）', show_default=True)
@click.option('--threshold', default=2.0, type=float, help='盛り上がりと判定するしきい値（平均値に対する倍率）', show_default=True)
@click.option('--duration', default=15.0, type=float, help='切り出し動画の長さ（秒）', show_default=True)
@click.option('--offset', default=10.0, type=float, help='ピークから何秒遡って切り出しを開始するか', show_default=True)
@click.option('--output-dir', default='output', type=str, help='切り出した動画の保存先ディレクトリ', show_default=True)
@click.option('--fast', is_flag=True, help='キーフレームに合わせた高速な切り出しを行う（正確な秒数での切り出しは行いません）')
def clip(video_path, log_path, window, threshold, duration, offset, output_dir, fast):
    """動画とチャットログから見どころを抽出し、動画を切り出します。
    
    VIDEO_PATH: 解析対象の動画ファイルのパス。
    LOG_PATH: チャットログファイル（CSV または JSON）のパス。
    """
    click.echo(f"=== stream-clipper 処理開始 ===")
    click.echo(f"動画ファイル: {video_path}")
    click.echo(f"チャットログ: {log_path}")
    click.echo(f"出力フォルダ: {output_dir}")
    click.echo(f"高速カット: {'有効' if fast else '無効（再エンコードによる正確なカット）'}")
    click.echo(f"=================================")
    
    # パイプラインの作成と実行
    pipeline = ClipPipeline(
        window_sec=window,
        threshold_multiplier=threshold,
        duration_sec=duration,
        offset_sec=offset,
        accurate_cut=not fast
    )
    
    try:
        pipeline.run(
            video_path=video_path,
            log_path=log_path,
            output_dir=output_dir
        )
        click.echo("=== 処理が正常に完了しました ===")
    except Exception as e:
        click.echo(f"\nエラーが発生しました: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    main()
