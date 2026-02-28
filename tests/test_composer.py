"""PageComposer のテスト。"""

from pathlib import Path

import pytest
from PIL import Image

from novelmanga.composer import PAGE_HEIGHT, PAGE_WIDTH, PageComposer
from novelmanga.models import Panel, PanelType, Scene


def _panel(
    n: int = 1,
    panel_type: PanelType = PanelType.ACTION,
    dialogue: list[str] | None = None,
    narration: str | None = None,
) -> Panel:
    return Panel(
        panel_number=n,
        panel_type=panel_type,
        visual_description="Test visual description",
        dialogue=dialogue or [],
        narration=narration,
    )


def _scene(n_panels: int, layout: str = "standard") -> Scene:
    return Scene(
        scene_number=1,
        source_text="",
        panels=[_panel(i + 1) for i in range(n_panels)],
        page_layout=layout,
    )


class TestPageComposer:
    def setup_method(self):
        self.composer = PageComposer()

    # --- compose_page 基本 ---

    def test_returns_pil_image(self):
        scene = _scene(2)
        page = self.composer.compose_page(scene, [None, None])
        assert isinstance(page, Image.Image)

    def test_correct_page_size(self):
        scene = _scene(1)
        page = self.composer.compose_page(scene, [None])
        assert page.size == (PAGE_WIDTH, PAGE_HEIGHT)

    def test_grayscale_mode(self):
        scene = _scene(1)
        page = self.composer.compose_page(scene, [None])
        assert page.mode == "L"

    def test_empty_scene_returns_blank_page(self):
        scene = Scene(scene_number=1, source_text="", panels=[], page_layout="standard")
        page = self.composer.compose_page(scene, [])
        assert isinstance(page, Image.Image)

    # --- パネル画像の合成 ---

    def test_compose_with_real_image(self):
        scene = _scene(1)
        img = Image.new("RGB", (200, 200), color="gray")
        page = self.composer.compose_page(scene, [img])
        assert isinstance(page, Image.Image)

    def test_compose_partial_images(self):
        """画像が一部 None でも落ちないこと。"""
        scene = _scene(3)
        img = Image.new("RGB", (100, 100), color="black")
        page = self.composer.compose_page(scene, [img, None, img])
        assert isinstance(page, Image.Image)

    # --- 吹き出し・ナレーション ---

    def test_dialogue_panel_renders(self):
        panel = _panel(1, PanelType.DIALOGUE, dialogue=["こんにちは！"])
        scene = Scene(scene_number=1, source_text="", panels=[panel], page_layout="standard")
        page = self.composer.compose_page(scene, [None])
        assert isinstance(page, Image.Image)

    def test_narration_panel_renders(self):
        panel = _panel(1, PanelType.NARRATION, narration="物語は続く...")
        scene = Scene(scene_number=1, source_text="", panels=[panel], page_layout="standard")
        page = self.composer.compose_page(scene, [None])
        assert isinstance(page, Image.Image)

    def test_multiple_dialogue_lines(self):
        panel = _panel(1, PanelType.DIALOGUE, dialogue=["セリフ1", "セリフ2", "セリフ3"])
        scene = Scene(scene_number=1, source_text="", panels=[panel], page_layout="standard")
        page = self.composer.compose_page(scene, [None])
        assert isinstance(page, Image.Image)

    # --- レイアウト計算 ---

    @pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
    def test_layout_returns_correct_count(self, n):
        rects = self.composer._calculate_layout(n, "standard")
        assert len(rects) == n

    @pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
    def test_layout_rects_are_valid(self, n):
        rects = self.composer._calculate_layout(n, "standard")
        for x1, y1, x2, y2 in rects:
            assert x2 > x1, f"Panel {n}: x2 ({x2}) <= x1 ({x1})"
            assert y2 > y1, f"Panel {n}: y2 ({y2}) <= y1 ({y1})"
            assert x1 >= 0
            assert y1 >= 0
            assert x2 <= PAGE_WIDTH
            assert y2 <= PAGE_HEIGHT

    def test_action_layout_3_panels(self):
        rects = self.composer._calculate_layout(3, "action")
        assert len(rects) == 3
        # action レイアウトでは最初のパネルが縦に大きい
        _, y1_top, _, y2_top = rects[0]
        _, y1_b1, _, y2_b1 = rects[1]
        assert (y2_top - y1_top) > (y2_b1 - y1_b1)

    # --- ページ保存 ---

    def test_save_page_creates_file(self, tmp_path):
        scene = _scene(1)
        page = self.composer.compose_page(scene, [None])
        out = tmp_path / "page_001.png"
        self.composer.save_page(page, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_save_page_creates_parent_dirs(self, tmp_path):
        scene = _scene(1)
        page = self.composer.compose_page(scene, [None])
        out = tmp_path / "deep" / "nested" / "page.png"
        self.composer.save_page(page, out)
        assert out.exists()

    def test_save_page_valid_png(self, tmp_path):
        scene = _scene(2)
        page = self.composer.compose_page(scene, [None, None])
        out = tmp_path / "test.png"
        self.composer.save_page(page, out)
        loaded = Image.open(out)
        assert loaded.size == (PAGE_WIDTH, PAGE_HEIGHT)
