"""青空文庫形式テキストのパーサー。"""

from __future__ import annotations

import re
from pathlib import Path


class AozoraBunkoParser:
    """青空文庫形式テキストを解析し、クリーンなプレーンテキストに変換する。"""

    # ｜漢字《かんじ》 → 漢字
    _PIPE_RUBY = re.compile(r"｜([^《》\n]+)《[^《》\n]+》")
    # 漢字《かんじ》 → 漢字
    _BARE_RUBY = re.compile(r"《[^《》\n]+》")
    # ［＃...］ 注釈記号
    _ANNOTATION = re.compile(r"［＃[^］]*］")
    # 区切り線（ヘッダー・フッター）
    _SEPARATOR = re.compile(r"-{20,}")
    # 3行以上の連続空行
    _MULTI_BLANK = re.compile(r"\n{3,}")

    def parse_file(self, filepath: str | Path) -> str:
        """ファイルを読み込み、クリーンテキストを返す。"""
        path = Path(filepath)
        text = self._read_with_encoding(path)
        return self.clean_text(text)

    def _read_with_encoding(self, path: Path) -> str:
        for encoding in ("utf-8", "utf-8-sig", "shift_jis", "cp932"):
            try:
                return path.read_text(encoding=encoding)
            except (UnicodeDecodeError, LookupError):
                continue
        raise ValueError(f"Cannot decode file: {path}")

    def clean_text(self, text: str) -> str:
        """青空文庫特有のマークアップを除去する。"""
        # ヘッダーとフッターを除去（区切り線で囲まれた本文だけを取得）
        # 典型的な青空文庫構造: ヘッダー | [注釈] | 本文 [| フッター]
        parts = self._SEPARATOR.split(text)
        if len(parts) == 2:
            # 区切り線1本: header | body
            text = parts[1]
        elif len(parts) >= 3:
            # 区切り線2本以上: header | notes | body [| footer]
            # 本文は parts[2] から始まる（フッターがあれば最後を除く）
            body_end = len(parts) if len(parts) <= 3 else len(parts) - 1
            text = "\n\n".join(parts[2:body_end])

        # ルビ除去（｜記号付き）
        text = self._PIPE_RUBY.sub(r"\1", text)
        # ルビ除去（記号なし）
        text = self._BARE_RUBY.sub("", text)
        # 注釈除去
        text = self._ANNOTATION.sub("", text)
        # 行頭の全角スペース（字下げ）を除去
        text = re.sub(r"^　+", "", text, flags=re.MULTILINE)
        # 連続空行を2行に圧縮
        text = self._MULTI_BLANK.sub("\n\n", text)

        return text.strip()

    def split_paragraphs(self, text: str) -> list[str]:
        """空行区切りで段落リストに分割する。"""
        return [p.strip() for p in text.split("\n\n") if p.strip()]

    def chunk_for_analysis(self, text: str, chunk_size: int = 2000) -> list[str]:
        """Claude API に送る単位でテキストをチャンク分割する。

        段落の途中で切らないよう、段落単位でチャンクを作成する。
        """
        paragraphs = self.split_paragraphs(text)
        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for para in paragraphs:
            para_len = len(para)
            if current and current_len + para_len > chunk_size:
                chunks.append("\n\n".join(current))
                current = [para]
                current_len = para_len
            else:
                current.append(para)
                current_len += para_len

        if current:
            chunks.append("\n\n".join(current))

        return chunks
