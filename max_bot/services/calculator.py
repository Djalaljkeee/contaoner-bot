from dataclasses import dataclass, field

# ── Pricing config (edit here without touching handler code) ──────────────────

BASE_PRICES: dict[str, int] = {
    "20 футов (6×2.4 м)": 168_000,
    "40 футов (12×2.4 м)": 285_000,
}

INSULATION_DELTA: dict[str, int] = {
    "100 мм (базовое)": 0,
    "150 мм (+25 000 ₽)": 25_000,
    "200 мм (+55 000 ₽)": 55_000,
}

FINISH_DELTA: dict[str, int] = {
    "Эконом (базовая)": 0,
    "Стандарт (+40 000 ₽)": 40_000,
    "Премиум (+90 000 ₽)": 90_000,
}

OPTIONS_DELTA: dict[str, int] = {
    "⚡ Электрика под ключ (+45 000 ₽)": 45_000,
    "🚿 Санузел с душем (+85 000 ₽)": 85_000,
    "🌿 Терраса (+60 000 ₽)": 60_000,
    "❄️ Кондиционер (+35 000 ₽)": 35_000,
}

# ── Labels for display ────────────────────────────────────────────────────────

SIZE_LABELS = list(BASE_PRICES.keys())
INSULATION_LABELS = list(INSULATION_DELTA.keys())
FINISH_LABELS = list(FINISH_DELTA.keys())
OPTION_LABELS = list(OPTIONS_DELTA.keys())


@dataclass
class CalcConfig:
    size: str = ""
    insulation: str = ""
    finish: str = ""
    options: list[str] = field(default_factory=list)

    def total(self) -> int:
        base = BASE_PRICES.get(self.size, 0)
        ins = INSULATION_DELTA.get(self.insulation, 0)
        fin = FINISH_DELTA.get(self.finish, 0)
        opts = sum(OPTIONS_DELTA.get(o, 0) for o in self.options)
        return base + ins + fin + opts

    def summary(self) -> str:
        opts_text = ", ".join(self.options) if self.options else "нет"
        return (
            f"📐 Размер: {self.size}\n"
            f"🧱 Утепление: {self.insulation}\n"
            f"🎨 Отделка: {self.finish}\n"
            f"➕ Опции: {opts_text}\n\n"
            f"💰 Итого: {self.total():,} ₽".replace(",", " ")
        )

    def to_dict(self) -> dict:
        return {
            "size": self.size,
            "insulation": self.insulation,
            "finish": self.finish,
            "options": self.options,
            "total": self.total(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CalcConfig":
        return cls(
            size=d.get("size", ""),
            insulation=d.get("insulation", ""),
            finish=d.get("finish", ""),
            options=d.get("options", []),
        )
