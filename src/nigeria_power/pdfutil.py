"""Read PDF text and collapse whitespace so phrases can be matched.

pypdf handles most of these reports. A few publisher PDFs exceed its token
budget; those fall back to poppler's pdftotext when it is installed.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import LimitReachedError, PdfReadError


def normalise(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", text)


def _pdftotext(path: str) -> str:
    binary = shutil.which("pdftotext")
    if not binary:
        raise RuntimeError(
            f"Could not read {path} with pypdf, and pdftotext is not installed. "
            "Install poppler-utils and run again."
        )
    completed = subprocess.run(
        [binary, "-q", path, "-"],
        check=True,
        capture_output=True,
    )
    return completed.stdout.decode("utf-8", errors="replace")


@lru_cache(maxsize=64)
def pdf_text(path: str) -> str:
    try:
        reader = PdfReader(path)
        parts: list[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        text = "\n".join(parts)
        if len(text.strip()) < 200:
            raise PdfReadError("extracted text was almost empty")
        return normalise(text)
    except (LimitReachedError, PdfReadError, Exception) as exc:
        # A genuine empty or hostile PDF should still surface if pdftotext
        # is missing. Other extraction failures try the system tool once.
        if isinstance(exc, RuntimeError):
            raise
        try:
            return normalise(_pdftotext(path))
        except Exception:
            raise exc


def require_phrase(path: Path, pattern: str, label: str) -> re.Match[str]:
    text = pdf_text(str(path))
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        raise RuntimeError(
            f"Could not find {label} in {path.name}. "
            "The PDF may have changed, or text extraction failed. "
            "Refusing to continue with a missing figure."
        )
    return match


def parse_number(token: str) -> float:
    return float(token.replace(",", "").replace(" ", ""))
