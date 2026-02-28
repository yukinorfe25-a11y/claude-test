"""Pillow を使ったページ合成・吹き出し配置モジュール。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from .models import Panel, Scene

PAGE_WIDTH = 1080
PAGE_HEIGHT = 1528
PANEL_MARGIN = 12
BUBBLE_PAD = 10

# 日本語フォントの候補（優先順）
_FONT_CANDIDATES = [
    # Windows
    "C:/Windows/Fonts/YuGothM.ttc",
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
    # macOS
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/Library/Fonts/NotoSansCJK-Regular.ttc",
    # Linux
    "/usr/share/fonts/truetype/noto/NotoSansCJKjp-Regular.otf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """日本語対応フォントを読み込む。見つからない場合はデフォルトを返す。"""
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


class PageComposer:
    """シーンデータとパネル画像からマンガページ画像を合成する。"""

    def __init__(self, font_path: Optional[str] = None) -> None:
        if font_path:
            _FONT_CANDIDATES.insert(0, font_path)
        self._font_dialogue = _load_font(20)
        self._font_narration = _load_font(17)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compose_page(
        self,
        scene: Scene,
        panel_images: list[Optional[Image.Image]],
    ) -> Image.Image:
        """シーンとパネル画像リストからページ画像を生成する。"""
        page = Image.new("L", (PAGE_WIDTH, PAGE_HEIGHT), color=255)
        draw = ImageDraw.Draw(page)

        panels = scene.panels
        if not panels:
            return page

        rects = self._calculate_layout(len(panels), scene.page_layout)

        for i, (panel, rect) in enumerate(zip(panels, rects)):
            self._draw_panel(
                page,
                draw,
                panel,
                rect,
                panel_images[i] if i < len(panel_images) else None,
            )

        return page

    def save_page(self, page: Image.Image, output_path: str | Path) -> None:
        """ページ画像を PNG 形式で保存する。"""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        page.save(str(out), "PNG")

    # ------------------------------------------------------------------
    # Panel rendering
    # ------------------------------------------------------------------

    def _draw_panel(
        self,
        page: Image.Image,
        draw: ImageDraw.ImageDraw,
        panel: Panel,
        rect: tuple[int, int, int, int],
        img: Optional[Image.Image],
    ) -> None:
        x1, y1, x2, y2 = rect
        pw, ph = x2 - x1, y2 - y1

        # 背景（薄いグレー） + 枠線
        draw.rectangle(rect, fill=245, outline=0, width=3)

        # 背景画像
        if img:
            bg = img.convert("L").resize((pw - 6, ph - 6), Image.LANCZOS)
            page.paste(bg, (x1 + 3, y1 + 3))

        # ナレーション
        if panel.narration:
            self._draw_narration_box(draw, panel.narration, rect)

        # 吹き出し
        for idx, line in enumerate(panel.dialogue[:3]):
            self._draw_speech_bubble(draw, line, rect, idx)

    # ------------------------------------------------------------------
    # Speech bubble & narration
    # ------------------------------------------------------------------

    def _draw_speech_bubble(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        panel_rect: tuple[int, int, int, int],
        index: int,
    ) -> None:
        x1, y1, x2, y2 = panel_rect
        pw = x2 - x1
        bw = min(int(pw * 0.55), 220)
        bh = 52
        offset = index * (bh + 4)
        bx = x2 - bw - PANEL_MARGIN
        by = y2 - bh - PANEL_MARGIN - offset
        if by < y1 + PANEL_MARGIN:
            return
        bubble = (bx, by, bx + bw, by + bh)
        draw.ellipse(bubble, fill=255, outline=0, width=2)
        self._draw_centered_text(draw, text, bubble, self._font_dialogue)

    def _draw_narration_box(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        panel_rect: tuple[int, int, int, int],
    ) -> None:
        x1, y1, x2, _ = panel_rect
        box = (x1 + PANEL_MARGIN, y1 + PANEL_MARGIN, x2 - PANEL_MARGIN, y1 + PANEL_MARGIN + 38)
        draw.rectangle(box, fill=220, outline=0, width=1)
        self._draw_centered_text(draw, text, box, self._font_narration)

    def _draw_centered_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        rect: tuple[int, int, int, int],
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    ) -> None:
        x1, y1, x2, y2 = rect
        max_w = x2 - x1 - BUBBLE_PAD * 2

        # テキストを最大幅に収まるよう切り詰め
        display = text
        try:
            while len(display) > 1:
                bbox = draw.textbbox((0, 0), display, font=font)
                if bbox[2] - bbox[0] <= max_w:
                    break
                display = display[:-1]
            bbox = draw.textbbox((0, 0), display, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        except AttributeError:
            tw, th = draw.textsize(display, font=font)  # type: ignore[attr-defined]

        tx = x1 + (x2 - x1 - tw) // 2
        ty = y1 + (y2 - y1 - th) // 2
        draw.text((tx, ty), display, fill=0, font=font)

    # ------------------------------------------------------------------
    # Layout engine
    # ------------------------------------------------------------------

    def _calculate_layout(
        self, n: int, layout_type: str
    ) -> list[tuple[int, int, int, int]]:
        """n コマのパネル矩形リストを返す。"""
        m = PANEL_MARGIN
        W, H = PAGE_WIDTH, PAGE_HEIGHT

        if n == 1:
            return [(m, m, W - m, H - m)]

        if n == 2:
            mid = H // 2
            return [
                (m, m, W - m, mid - m),
                (m, mid + m, W - m, H - m),
            ]

        if n == 3:
            if layout_type == "action":
                top = int(H * 0.58)
                mid = W // 2
                return [
                    (m, m, W - m, top),
                    (m, top + m, mid - m, H - m),
                    (mid + m, top + m, W - m, H - m),
                ]
            row = H // 3
            return [
                (m, m, W - m, row - m),
                (m, row + m, W - m, row * 2 - m),
                (m, row * 2 + m, W - m, H - m),
            ]

        if n == 4:
            mw, mh = W // 2, H // 2
            return [
                (m, m, mw - m, mh - m),
                (mw + m, m, W - m, mh - m),
                (m, mh + m, mw - m, H - m),
                (mw + m, mh + m, W - m, H - m),
            ]

        if n == 5:
            row = H // 2
            tw = W // 3
            return [
                (m, m, W // 2 - m, row - m),
                (W // 2 + m, m, W - m, row - m),
                (m, row + m, tw - m, H - m),
                (tw + m, row + m, tw * 2 - m, H - m),
                (tw * 2 + m, row + m, W - m, H - m),
            ]

        # 6 コマ（デフォルト）
        mw, th = W // 2, H // 3
        return [
            (m, m, mw - m, th - m),
            (mw + m, m, W - m, th - m),
            (m, th + m, mw - m, th * 2 - m),
            (mw + m, th + m, W - m, th * 2 - m),
            (m, th * 2 + m, mw - m, H - m),
            (mw + m, th * 2 + m, W - m, H - m),
        ]
