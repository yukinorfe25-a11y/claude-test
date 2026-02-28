"""ImageGenerator のテスト（Gemini API はモック）。"""

import base64
import io
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image


def _make_png_bytes(size: tuple[int, int] = (100, 100)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color="white").save(buf, format="PNG")
    return buf.getvalue()


def _make_mock_client(png_bytes: bytes) -> MagicMock:
    """成功レスポンスを返すモッククライアントを作成する。"""
    mock_inline = MagicMock()
    mock_inline.mime_type = "image/png"
    mock_inline.data = png_bytes

    mock_part = MagicMock()
    mock_part.inline_data = mock_inline

    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    return mock_client


class TestImageGenerator:
    @patch("google.genai.Client")
    def test_returns_image_on_success(self, mock_client_cls):
        from novelmanga.generator import ImageGenerator

        png_bytes = _make_png_bytes()
        mock_client_cls.return_value = _make_mock_client(png_bytes)

        gen = ImageGenerator(api_key="test")
        result = gen.generate_panel_image("A dark room", 256, 256)

        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == (256, 256)

    @patch("google.genai.Client")
    def test_handles_base64_encoded_data(self, mock_client_cls):
        from novelmanga.generator import ImageGenerator

        png_bytes = _make_png_bytes()
        # base64 文字列として返ってくるケース
        mock_inline = MagicMock()
        mock_inline.mime_type = "image/png"
        mock_inline.data = base64.b64encode(png_bytes).decode()

        mock_part = MagicMock()
        mock_part.inline_data = mock_inline

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        gen = ImageGenerator(api_key="test")
        result = gen.generate_panel_image("A bright room")

        assert result is not None
        assert isinstance(result, Image.Image)

    @patch("google.genai.Client")
    def test_returns_none_on_api_error(self, mock_client_cls):
        from novelmanga.generator import ImageGenerator

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API unavailable")
        mock_client_cls.return_value = mock_client

        gen = ImageGenerator(api_key="test")
        result = gen.generate_panel_image("Any description")

        assert result is None

    @patch("google.genai.Client")
    def test_returns_none_when_no_image_part(self, mock_client_cls):
        from novelmanga.generator import ImageGenerator

        # テキストのみ返ってくるケース（inline_data が None）
        mock_part = MagicMock()
        mock_part.inline_data = None

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        gen = ImageGenerator(api_key="test")
        result = gen.generate_panel_image("Description")

        assert result is None

    @patch("google.genai.Client")
    def test_custom_size(self, mock_client_cls):
        from novelmanga.generator import ImageGenerator

        png_bytes = _make_png_bytes((50, 50))
        mock_client_cls.return_value = _make_mock_client(png_bytes)

        gen = ImageGenerator(api_key="test")
        result = gen.generate_panel_image("Description", width=300, height=400)

        assert result is not None
        assert result.size == (300, 400)

    @patch("google.genai.Client")
    def test_manga_style_appended_to_prompt(self, mock_client_cls):
        from novelmanga.generator import ImageGenerator, _MANGA_STYLE

        png_bytes = _make_png_bytes()
        mock_client = _make_mock_client(png_bytes)
        mock_client_cls.return_value = mock_client

        gen = ImageGenerator(api_key="test")
        gen.generate_panel_image("A samurai scene")

        call_kwargs = mock_client.models.generate_content.call_args
        contents = call_kwargs.kwargs.get("contents") or call_kwargs.args[1] if len(call_kwargs.args) > 1 else call_kwargs.kwargs["contents"]
        assert "A samurai scene" in contents
        assert _MANGA_STYLE in contents
