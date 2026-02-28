"""SceneAnalyzer のテスト（Claude API はモック）。"""

import json
from unittest.mock import MagicMock, patch

import pytest

from novelmanga.analyzer import SceneAnalyzer
from novelmanga.models import Panel, PanelType, Scene

_VALID_JSON = json.dumps(
    {
        "scenes": [
            {
                "scene_number": 1,
                "page_layout": "standard",
                "panels": [
                    {
                        "panel_number": 1,
                        "panel_type": "establishing",
                        "visual_description": "A dimly lit room with a lone lamp",
                        "dialogue": [],
                        "narration": "物語の始まり。",
                    },
                    {
                        "panel_number": 2,
                        "panel_type": "dialogue",
                        "visual_description": "Close-up of a young man's face",
                        "dialogue": ["恥の多い生涯を送って来ました。"],
                        "narration": None,
                    },
                ],
            }
        ]
    }
)


class TestSceneAnalyzerParsing:
    """API を呼ばない純粋なパース処理のテスト。"""

    def _analyzer(self) -> SceneAnalyzer:
        obj = SceneAnalyzer.__new__(SceneAnalyzer)
        return obj

    def test_parse_valid_json(self):
        a = self._analyzer()
        scenes = a._parse_response(_VALID_JSON)
        assert len(scenes) == 1
        assert len(scenes[0].panels) == 2

    def test_parse_json_in_code_block(self):
        a = self._analyzer()
        wrapped = f"```json\n{_VALID_JSON}\n```"
        scenes = a._parse_response(wrapped)
        assert len(scenes) == 1

    def test_parse_json_with_preamble(self):
        a = self._analyzer()
        text = f"以下が脚本です：\n\n{_VALID_JSON}"
        scenes = a._parse_response(text)
        assert len(scenes) == 1

    def test_parse_empty_string_returns_empty(self):
        a = self._analyzer()
        assert a._parse_response("") == []

    def test_parse_invalid_json_returns_empty(self):
        a = self._analyzer()
        assert a._parse_response("これは JSON ではありません") == []

    def test_panel_type_mapping(self):
        a = self._analyzer()
        data = {
            "scenes": [
                {
                    "scene_number": 1,
                    "page_layout": "action",
                    "panels": [
                        {
                            "panel_number": 1,
                            "panel_type": "action",
                            "visual_description": "Fight scene",
                            "dialogue": [],
                            "narration": None,
                        }
                    ],
                }
            ]
        }
        scenes = a._build_scenes(data)
        assert scenes[0].panels[0].panel_type == PanelType.ACTION

    def test_unknown_panel_type_defaults_to_action(self):
        a = self._analyzer()
        data = {
            "scenes": [
                {
                    "scene_number": 1,
                    "page_layout": "standard",
                    "panels": [
                        {
                            "panel_number": 1,
                            "panel_type": "unknown_xyz",
                            "visual_description": "Something",
                            "dialogue": [],
                            "narration": None,
                        }
                    ],
                }
            ]
        }
        scenes = a._build_scenes(data)
        assert scenes[0].panels[0].panel_type == PanelType.ACTION

    def test_dialogue_and_narration_preserved(self):
        a = self._analyzer()
        scenes = a._parse_response(_VALID_JSON)
        panel2 = scenes[0].panels[1]
        assert panel2.dialogue == ["恥の多い生涯を送って来ました。"]
        assert panel2.narration is None

        panel1 = scenes[0].panels[0]
        assert panel1.narration == "物語の始まり。"

    def test_multiple_scenes(self):
        a = self._analyzer()
        data = {
            "scenes": [
                {
                    "scene_number": i,
                    "page_layout": "standard",
                    "panels": [
                        {
                            "panel_number": 1,
                            "panel_type": "narration",
                            "visual_description": f"Scene {i}",
                            "dialogue": [],
                            "narration": None,
                        }
                    ],
                }
                for i in range(1, 4)
            ]
        }
        scenes = a._build_scenes(data)
        assert len(scenes) == 3


class TestSceneAnalyzerWithMock:
    """Claude API をモックした統合テスト。"""

    @patch("anthropic.Anthropic")
    def test_analyze_chunk_returns_scenes(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        # stream のコンテキストマネージャをモック
        mock_stream = MagicMock()
        mock_final = MagicMock()
        text_block = MagicMock()
        text_block.text = _VALID_JSON
        mock_final.content = [text_block]
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_stream.get_final_message.return_value = mock_final
        mock_client.messages.stream.return_value = mock_stream

        analyzer = SceneAnalyzer(api_key="test-key")
        scenes = analyzer.analyze_chunk("テストテキスト")

        assert len(scenes) == 1
        assert len(scenes[0].panels) == 2
        mock_client.messages.stream.assert_called_once()

    @patch("anthropic.Anthropic")
    def test_analyze_chunk_invalid_response_returns_empty(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_stream = MagicMock()
        mock_final = MagicMock()
        text_block = MagicMock()
        text_block.text = "申し訳ありませんが、処理できません。"
        mock_final.content = [text_block]
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_stream.get_final_message.return_value = mock_final
        mock_client.messages.stream.return_value = mock_stream

        analyzer = SceneAnalyzer(api_key="test-key")
        scenes = analyzer.analyze_chunk("テストテキスト")

        assert scenes == []
