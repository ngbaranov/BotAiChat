from __future__ import annotations
from typing import Optional

# Минимум зависимостей: без chardet. Пытаемся несколькими кодировками.
CANDIDATE_ENCODINGS = ("utf-8", "utf-16", "cp1251", "latin-1")

def read_text_file(path: str, max_chars: Optional[int] = None) -> str:
    """
    Читает .txt/.md с попыткой разных кодировок.
    Возвращает строку (при ошибках символы заменяются).
    """
    data: Optional[bytes] = None
    with open(path, "rb") as f:
        data = f.read()

    text: Optional[str] = None
    for enc in CANDIDATE_ENCODINGS:
        try:
            text = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if text is None:
        # Последний шанс — 'utf-8' с заменой битых символов
        text = data.decode("utf-8", errors="replace")

    text = text.strip()
    if max_chars is not None and max_chars > 0:
        text = text[:max_chars]
    return text
