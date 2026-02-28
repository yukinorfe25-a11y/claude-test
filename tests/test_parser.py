"""AozoraBunkoParser のテスト。"""

import pytest
from novelmanga.parser import AozoraBunkoParser


SAMPLE_WITH_SEPARATOR = """\
太宰　治
人間失格
-------------------------------------------------------
【テキスト中に現れる記号について】
-------------------------------------------------------
　はしがき

　私はその男の写真を三葉《さんよう》、見たことがある。
　一葉《いちよう》は、その男の、幼年時代とでも言うべき頃の写真で。
"""


class TestAozoraBunkoParser:
    def setup_method(self):
        self.parser = AozoraBunkoParser()

    # --- clean_text ---

    def test_remove_bare_ruby(self):
        result = self.parser.clean_text("漢字《かんじ》のテスト")
        assert "《かんじ》" not in result
        assert "漢字" in result

    def test_remove_pipe_ruby(self):
        result = self.parser.clean_text("｜特殊《とくしゅ》ルビ")
        assert "《とくしゅ》" not in result
        assert "特殊" in result

    def test_remove_annotations(self):
        result = self.parser.clean_text("テキスト［＃注釈記号］本文")
        assert "［＃注釈記号］" not in result
        assert "テキスト" in result
        assert "本文" in result

    def test_remove_leading_fullwidth_space(self):
        result = self.parser.clean_text("　字下げされた行")
        assert not result.startswith("　")

    def test_compress_multiple_blank_lines(self):
        text = "段落1\n\n\n\n\n段落2"
        result = self.parser.clean_text(text)
        assert "\n\n\n" not in result

    def test_extract_body_between_separators(self):
        result = self.parser.clean_text(SAMPLE_WITH_SEPARATOR)
        # ヘッダー部分が除去され、本文が含まれる
        assert "はしがき" in result
        assert "私はその男" in result

    def test_strip_result(self):
        result = self.parser.clean_text("  \n\nテキスト\n\n  ")
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    # --- split_paragraphs ---

    def test_split_paragraphs_basic(self):
        text = "段落1\n\n段落2\n\n段落3"
        paragraphs = self.parser.split_paragraphs(text)
        assert len(paragraphs) == 3

    def test_split_paragraphs_removes_empty(self):
        text = "段落1\n\n\n\n段落2"
        paragraphs = self.parser.split_paragraphs(text)
        assert all(p for p in paragraphs)

    def test_split_paragraphs_strips_whitespace(self):
        text = "  段落1  \n\n  段落2  "
        paragraphs = self.parser.split_paragraphs(text)
        for p in paragraphs:
            assert p == p.strip()

    # --- chunk_for_analysis ---

    def test_chunk_creates_multiple_chunks(self):
        paragraphs = [f"段落{i}。" * 5 for i in range(20)]
        text = "\n\n".join(paragraphs)
        chunks = self.parser.chunk_for_analysis(text, chunk_size=100)
        assert len(chunks) > 1

    def test_chunk_preserves_all_text(self):
        paragraphs = [f"段落{i}テキスト" for i in range(10)]
        text = "\n\n".join(paragraphs)
        chunks = self.parser.chunk_for_analysis(text, chunk_size=50)
        combined = "\n\n".join(chunks)
        for para in paragraphs:
            assert para in combined

    def test_chunk_single_when_small(self):
        text = "短いテキスト\n\n２番目の段落"
        chunks = self.parser.chunk_for_analysis(text, chunk_size=5000)
        assert len(chunks) == 1

    # --- parse_file ---

    def test_parse_file_utf8(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("テスト漢字《かんじ》テキスト", encoding="utf-8")
        result = self.parser.parse_file(f)
        assert isinstance(result, str)
        assert "《かんじ》" not in result

    def test_parse_file_not_found(self):
        with pytest.raises(Exception):
            self.parser.parse_file("/nonexistent/path/file.txt")
