from dataclasses import dataclass, field


@dataclass
class StageResult:
    processed: int = 0
    written: int = 0
    rejected: int = 0
    model: str = ""
    tokens: int = 0
    cost: float = 0.0
    error: str = ""
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "processed": self.processed,
            "written": self.written,
            "rejected": self.rejected,
            "model": self.model,
            "tokens": self.tokens,
            "cost": self.cost,
            "error": self.error,
            "details": self.details,
        }
