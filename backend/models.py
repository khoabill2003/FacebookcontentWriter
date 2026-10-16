"""Các kiểu dữ liệu dùng chung."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ProductData(BaseModel):
    """Thông tin sản phẩm; trường không xác định để None (không bịa)."""

    name: Optional[str] = None
    brand: Optional[str] = None
    abv: Optional[str] = None
    volume: Optional[str] = None


class Post(BaseModel):
    """Một bài Facebook."""

    title: str = ""
    body: str = ""
    slogan: str = ""
    cta: str = ""
    contact: str = ""
    warning: str = ""
    hashtags: list[str] = Field(default_factory=list)

    def full_text(self) -> str:
        """Ghép toàn bộ nội dung thành một chuỗi."""
        parts = [self.title, self.body, self.slogan, self.cta, self.contact, self.warning, " ".join(self.hashtags)]
        return "\n\n".join(p for p in parts if p)
