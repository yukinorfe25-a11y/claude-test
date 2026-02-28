"""Gemini API を使ったシーン分割・脚本生成モジュール。"""

from __future__ import annotations

import json
import re

from google import genai
from google.genai import types

from .models import Panel, PanelType, Scene

_SYSTEM_PROMPT = """あなたは小説を漫画の脚本に変換する専門家です。
与えられた小説テキストを漫画ページに変換するための脚本を生成してください。

以下の JSON 形式のみで出力してください（前後に余計なテキストを入れないこと）：

{
  "scenes": [
    {
      "scene_number": 1,
      "page_layout": "standard",
      "panels": [
        {
          "panel_number": 1,
          "panel_type": "establishing",
          "visual_description": "Detailed English description for image generation AI",
          "dialogue": ["セリフ1", "セリフ2"],
          "narration": "ナレーションテキスト（なければ null）"
        }
      ]
    }
  ]
}

ガイドライン：
- 各シーンは 1〜6 コマで構成（通常は 2〜4 コマ）
- visual_description は画像生成 AI 向けの英語プロンプト（詳細に）
- panel_type: "action" / "dialogue" / "narration" / "establishing"
- page_layout: "standard" / "action" / "emotional"
- 日本漫画スタイルを意識すること
- テキストの分量に応じて適切な数のシーンを生成すること"""


class SceneAnalyzer:
    """Gemini API を用いてテキストチャンクをシーン脚本に変換する。"""

    def __init__(self, api_key: str | None = None) -> None:
        self.client = genai.Client(api_key=api_key)

    def analyze_chunk(self, text_chunk: str) -> list[Scene]:
        """テキストチャンクを解析し、シーンリストを返す。"""
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
                max_output_tokens=8192,
            ),
            contents="以下の小説テキストを漫画の脚本に変換してください：\n\n"
            + text_chunk,
        )

        return self._parse_response(response.text)

    def _parse_response(self, response_text: str) -> list[Scene]:
        """レスポンステキストから JSON を抽出してシーンリストに変換する。"""
        # コードブロックを除去
        cleaned = re.sub(r"```(?:json)?\s*", "", response_text).strip()

        # JSON オブジェクトを抽出
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start == -1 or end <= start:
            print(f"Warning: No JSON found in response")
            return []

        try:
            data = json.loads(cleaned[start:end])
        except json.JSONDecodeError as e:
            print(f"Warning: JSON parse error: {e}")
            return []

        return self._build_scenes(data)

    def _build_scenes(self, data: dict) -> list[Scene]:
        """辞書データから Scene オブジェクトのリストを構築する。"""
        scenes: list[Scene] = []
        for scene_data in data.get("scenes", []):
            panels = [
                self._build_panel(p) for p in scene_data.get("panels", [])
            ]
            scenes.append(
                Scene(
                    scene_number=scene_data.get("scene_number", len(scenes) + 1),
                    source_text="",
                    panels=panels,
                    page_layout=scene_data.get("page_layout", "standard"),
                )
            )
        return scenes

    def _build_panel(self, data: dict) -> Panel:
        """辞書データから Panel オブジェクトを構築する。"""
        type_str = data.get("panel_type", "action")
        try:
            panel_type = PanelType(type_str)
        except ValueError:
            panel_type = PanelType.ACTION

        return Panel(
            panel_number=data.get("panel_number", 1),
            panel_type=panel_type,
            visual_description=data.get("visual_description", ""),
            dialogue=data.get("dialogue") or [],
            narration=data.get("narration") or None,
        )
