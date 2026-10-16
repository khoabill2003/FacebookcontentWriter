"""Lỗi dịch vụ phụ thuộc (Ollama/Qdrant/SearXNG)."""


class ServiceError(RuntimeError):
    """Dịch vụ bên ngoài không khả dụng hoặc trả lỗi."""

    def __init__(self, service: str, message: str) -> None:
        super().__init__(f"[{service}] {message}")
        self.service = service
