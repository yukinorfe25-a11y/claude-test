"""Gemini API を使ったパネル画像生成モジュール。

新しい google-genai SDK (google.genai) を使用。
"""

from __future__ import annotations

import io
import os
from typing import Optional

from PIL import Image

_MANGA_STYLE = (
    "manga style, black and white ink drawing, Japanese comic art, "
    "clean line art, detailed, high quality, monochrome"
)

_DEFAULT_MODEL = "gemini-2.0-flash-exp-image-generation"


class ImageGenerator:
    """Gemini API を用いてコマの背景画像を生成する。"""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = _DEFAULT_MODEL,
    ) -> None:
        from google import genai

        resolved_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self._client = genai.Client(api_key=resolved_key)
        self._model = model
        self._genai = genai

    def generate_panel_image(
        self,
        visual_description: str,
        width: int = 512,
        height: int = 512,
    ) -> Optional[Image.Image]:
        """visual_description に基づいてコマ画像を生成して返す。

        生成失敗時は None を返す（呼び出し元は None チェックすること）。
        """
        from google.genai import types

        prompt = f"{visual_description}, {_MANGA_STYLE}"

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            for part in response.candidates[0].content.parts:
                inline = getattr(part, "inline_data", None)
                if inline and getattr(inline, "mime_type", "").startswith("image/"):
                    raw = inline.data
                    # SDK が bytes を返す場合
                    if isinstance(raw, (bytes, bytearray)):
                        img = Image.open(io.BytesIO(raw))
                    else:
                        # base64 文字列で返ってくる場合
                        import base64
                        img = Image.open(io.BytesIO(base64.b64decode(raw)))
                    return img.resize((width, height), Image.LANCZOS)

        except Exception as e:
            print(f"Warning: Image generation failed: {e}")

        return None
