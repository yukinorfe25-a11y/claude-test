#!/usr/bin/env python3
"""output/ ディレクトリをスキャンして manga-manifest.json を生成する。

使い方:
    python scripts/generate_manifest.py
    python scripts/generate_manifest.py --output-dir output --pages-per-chapter 10
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def find_page_images(search_dir: Path) -> list[str]:
    """search_dir 内の page_*.png を番号順で返す。"""
    pages = sorted(
        p.name for p in search_dir.glob("page_*.png")
        if re.match(r"page_\d+\.png$", p.name)
    )
    return pages


def ensure_novel_subdir(output_dir: Path, novel_id: str) -> Path:
    """output_dir/{novel_id}/ サブディレクトリを作成し、
    ルートの page_*.png をそこに移動する。

    既にサブディレクトリに画像がある場合はスキップ。
    """
    novel_dir = output_dir / novel_id
    novel_dir.mkdir(exist_ok=True)

    # サブディレクトリに既に画像がある場合はスキップ
    if find_page_images(novel_dir):
        return novel_dir

    # ルートにある画像をサブディレクトリにコピー
    import shutil
    for page_file in output_dir.glob("page_*.png"):
        if re.match(r"page_\d+\.png$", page_file.name):
            dest = novel_dir / page_file.name
            if not dest.exists():
                shutil.copy2(page_file, dest)

    return novel_dir


def build_manifest(
    output_dir: Path,
    novel_id: str = "ningen_shikkaku",
    title: str = "人間失格",
    author: str = "太宰治",
    pages_per_chapter: int = 0,
) -> dict:
    """マニフェストJSONを構築する。

    pages_per_chapter=0 の場合、全ページを1章として扱う。
    """
    # サブディレクトリを作成し、画像を配置
    novel_dir = ensure_novel_subdir(output_dir, novel_id)
    pages = find_page_images(novel_dir)
    if not pages:
        raise FileNotFoundError(
            f"No page_*.png found in {output_dir} or {novel_dir}"
        )

    # 章に分割
    if pages_per_chapter > 0:
        chunks = [
            pages[i : i + pages_per_chapter]
            for i in range(0, len(pages), pages_per_chapter)
        ]
    else:
        chunks = [pages]

    chapters = []
    for idx, chunk in enumerate(chunks, 1):
        chapters.append(
            {
                "id": f"chapter_{idx:02d}",
                "title": f"第{idx}章" if len(chunks) > 1 else "全編",
                "pages": [f"{novel_id}/{p}" for p in chunk],
            }
        )

    cover = f"{novel_id}/{pages[0]}" if pages else ""

    manifest = {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "novels": [
            {
                "id": novel_id,
                "title": title,
                "author": author,
                "coverImage": cover,
                "chapters": chapters,
            }
        ],
    }
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="manga-manifest.json を生成")
    parser.add_argument(
        "--output-dir", "-d", default="output", help="ページ画像のディレクトリ"
    )
    parser.add_argument(
        "--pages-per-chapter",
        "-c",
        type=int,
        default=0,
        help="1章あたりのページ数（0=全ページ1章）",
    )
    parser.add_argument(
        "--novel-id", default="ningen_shikkaku", help="作品ID"
    )
    parser.add_argument("--title", default="人間失格", help="作品タイトル")
    parser.add_argument("--author", default="太宰治", help="著者名")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        print(f"Error: {output_dir} が存在しません。")
        print("先に python -m novelmanga でページを生成してください。")
        raise SystemExit(1)

    manifest = build_manifest(
        output_dir,
        novel_id=args.novel_id,
        title=args.title,
        author=args.author,
        pages_per_chapter=args.pages_per_chapter,
    )

    # output/ 直下に配置（HTTPサーバーのルートからアクセス可能に）
    manifest_path = output_dir / "manga-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

    total_pages = sum(len(ch["pages"]) for ch in manifest["novels"][0]["chapters"])
    total_chapters = len(manifest["novels"][0]["chapters"])
    print(f"[OK] {manifest_path} を生成しました")
    print(f"  作品: {args.title} ({args.novel_id})")
    print(f"  {total_chapters} 章, {total_pages} ページ")


if __name__ == "__main__":
    main()
