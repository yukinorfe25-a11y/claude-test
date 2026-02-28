"""NovelManga エントリーポイント。

使い方:
    python -m novelmanga data/sample/ningen_shikkaku.txt
    python -m novelmanga data/sample/ningen_shikkaku.txt -o output/ -p 5
    python -m novelmanga data/sample/ningen_shikkaku.txt --no-images
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m novelmanga",
        description="NovelManga: Aozora Bunko 小説 → 漫画ページ 自動変換ツール",
    )
    p.add_argument("input_file", help="青空文庫テキストファイルのパス")
    p.add_argument(
        "--output", "-o",
        default="output",
        help="出力ディレクトリ（デフォルト: output）",
    )
    p.add_argument(
        "--pages", "-p",
        type=int,
        default=None,
        metavar="N",
        help="生成するページ数の上限（省略時: 全件）",
    )
    p.add_argument(
        "--chunk-size",
        type=int,
        default=2000,
        metavar="CHARS",
        help="Claude API に送るテキストチャンクの文字数（デフォルト: 2000）",
    )
    p.add_argument(
        "--no-images",
        action="store_true",
        help="画像生成をスキップしてレイアウトのみ出力",
    )
    return p


def main() -> None:
    args = _build_parser().parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: ファイルが見つかりません: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # API キー確認
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "Warning: ANTHROPIC_API_KEY が未設定です。シーン解析がスキップされる場合があります。",
            file=sys.stderr,
        )
    skip_images = args.no_images or not os.environ.get("GOOGLE_API_KEY")
    if not args.no_images and not os.environ.get("GOOGLE_API_KEY"):
        print(
            "Warning: GOOGLE_API_KEY が未設定です。画像生成をスキップします。",
            file=sys.stderr,
        )

    print(f"入力: {input_path}")
    print(f"出力: {output_dir}")

    # --- モジュールをインポート ---
    from novelmanga.analyzer import SceneAnalyzer
    from novelmanga.composer import PageComposer
    from novelmanga.generator import ImageGenerator
    from novelmanga.parser import AozoraBunkoParser

    # Step 1: パース
    print("\n[1/4] 青空文庫テキストを解析中...")
    aozora_parser = AozoraBunkoParser()
    text = aozora_parser.parse_file(input_path)
    chunks = aozora_parser.chunk_for_analysis(text, chunk_size=args.chunk_size)

    if args.pages:
        chunks = chunks[: args.pages]
    print(f"  -> {len(chunks)} チャンク")

    # Step 2: シーン解析
    print("\n[2/4] Claude API でシーン解析中...")
    analyzer = SceneAnalyzer()
    all_scenes = []
    for i, chunk in enumerate(chunks, 1):
        print(f"  -> チャンク {i}/{len(chunks)}", end="", flush=True)
        scenes = analyzer.analyze_chunk(chunk)
        all_scenes.extend(scenes)
        print(f" ({len(scenes)} シーン)")
    print(f"  -> 合計 {len(all_scenes)} シーン")

    # Step 3: 画像生成
    print("\n[3/4] Gemini API でパネル画像を生成中...")
    all_panel_images: list[list] = []

    if skip_images:
        print("  -> スキップ（--no-images または GOOGLE_API_KEY 未設定）")
        all_panel_images = [[None] * len(s.panels) for s in all_scenes]
    else:
        image_gen = ImageGenerator()
        for si, scene in enumerate(all_scenes, 1):
            scene_imgs = []
            for pi, panel in enumerate(scene.panels, 1):
                print(f"  -> シーン {si}/{len(all_scenes)}, コマ {pi}/{len(scene.panels)}", end="", flush=True)
                img = image_gen.generate_panel_image(panel.visual_description)
                scene_imgs.append(img)
                print(" ✓" if img else " (スキップ)")
            all_panel_images.append(scene_imgs)

    # Step 4: ページ合成
    print("\n[4/4] ページを合成中...")
    composer = PageComposer()
    for i, (scene, panel_imgs) in enumerate(zip(all_scenes, all_panel_images), 1):
        page = composer.compose_page(scene, panel_imgs)
        out_path = output_dir / f"page_{i:03d}.png"
        composer.save_page(page, out_path)
        print(f"  -> 保存: {out_path}")

    print(f"\n完了！{len(all_scenes)} ページを {output_dir}/ に保存しました。")


if __name__ == "__main__":
    main()
