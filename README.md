# NovelManga

青空文庫形式の小説テキストを漫画ページに自動変換する Python ツール。

## 必要な環境

- Python 3.11+
- `ANTHROPIC_API_KEY` — シーン分割・脚本生成（Claude API）
- `GOOGLE_API_KEY` — パネル画像生成（Gemini API）

## インストール

```bash
pip install -e ".[dev]"
```

## 使い方

```bash
python -m novelmanga data/sample/ningen_shikkaku.txt
python -m novelmanga data/sample/ningen_shikkaku.txt -o output/ -p 5
python -m novelmanga data/sample/ningen_shikkaku.txt --no-images
```

## パイプライン

```
青空文庫テキスト
    │
    ▼ parser      — ルビ・注釈除去、チャンク分割
    ▼ analyzer    — Claude API でシーン分割・脚本（JSON）生成
    ▼ generator   — Gemini API でパネル背景画像生成
    ▼ composer    — Pillow でコマ配置・吹き出し合成
    │
    ▼ output/page_001.png ...
```

## テスト

```bash
pytest
pytest --cov=novelmanga
```
