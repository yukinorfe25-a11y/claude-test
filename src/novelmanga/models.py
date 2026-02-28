"""Data models for NovelManga pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class PanelType(Enum):
    ACTION = "action"
    DIALOGUE = "dialogue"
    NARRATION = "narration"
    ESTABLISHING = "establishing"


class PageLayout(Enum):
    STANDARD = "standard"
    ACTION = "action"
    EMOTIONAL = "emotional"


@dataclass
class Panel:
    panel_number: int
    panel_type: PanelType
    visual_description: str
    dialogue: list[str] = field(default_factory=list)
    narration: Optional[str] = None
    image_data: Optional[bytes] = None


@dataclass
class Scene:
    scene_number: int
    source_text: str
    panels: list[Panel] = field(default_factory=list)
    page_layout: str = "standard"


@dataclass
class MangaPage:
    page_number: int
    scene: Scene
    output_path: Optional[Path] = None
