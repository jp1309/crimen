"""Comprueba que GitHub Pages sirva exactamente el CSV versionado."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def normalizar_saltos(data: bytes) -> bytes:
    """Normaliza el unico cambio que GitHub Pages aplica al CSV versionado."""

    return data.replace(b"\r\n", b"\n")


def sha256_normalizado(data: bytes) -> str:
    return hashlib.sha256(normalizar_saltos(data)).hexdigest()


def comparar_csv(local: bytes, publicado: bytes) -> dict[str, object]:
    local_normalizado = normalizar_saltos(local)
    publicado_normalizado = normalizar_saltos(publicado)
    if local_normalizado != publicado_normalizado:
        raise ValueError(
            "El CSV publicado no coincide con el archivo versionado: "
            f"local={hashlib.sha256(local_normalizado).hexdigest()} "
            f"publico={hashlib.sha256(publicado_normalizado).hexdigest()}"
        )

    reader = csv.DictReader(io.StringIO(publicado_normalizado.decode("utf-8-sig")))
    rows = list(reader)
    if "fecha_infraccion" not in (reader.fieldnames or []):
        raise ValueError("El CSV publicado no contiene fecha_infraccion")
    dates = [row["fecha_infraccion"] for row in rows if row.get("fecha_infraccion")]
    return {
        "sha256": hashlib.sha256(publicado_normalizado).hexdigest(),
        "rows": len(rows),
        "max_date": max(dates) if dates else None,
    }


def verificar_publicacion(
    local_path: Path,
    public_url: str,
    commit: str,
    attempts: int = 30,
    delay_seconds: int = 10,
) -> dict[str, object]:
    local = local_path.read_bytes()
    separator = "&" if urllib.parse.urlparse(public_url).query else "?"
    url = f"{public_url}{separator}commit={urllib.parse.quote(commit)}"
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status != 200:
                    raise ValueError(f"GitHub Pages respondio HTTP {response.status}")
                result = comparar_csv(local, response.read())
            print(
                "GitHub Pages sirve el CSV actualizado: "
                f"{result['rows']:,} filas, max={result['max_date']}, sha256={result['sha256']}"
            )
            return result
        except (OSError, ValueError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(delay_seconds)

    raise RuntimeError(
        f"GitHub Pages no sirvio el CSV esperado despues de {attempts} intentos: {last_error}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", type=Path, default=Path("homicidios_clean.csv"))
    parser.add_argument("--url", default="https://jp1309.github.io/crimen/homicidios_clean.csv")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--attempts", type=int, default=30)
    parser.add_argument("--delay-seconds", type=int, default=10)
    args = parser.parse_args()
    verificar_publicacion(
        args.local,
        args.url,
        args.commit,
        attempts=args.attempts,
        delay_seconds=args.delay_seconds,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
