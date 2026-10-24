"""Diagnostica por que la red local no puede acceder a Datos Abiertos Ecuador.

Prueba en orden DNS, TCP, TLS y HTTP (con urllib y curl) contra el portal, la
API y la descarga del Excel anual. Cada capa que falla apunta a una causa
distinta: DNS de la red, filtrado por IP o pais, interceptacion TLS de un
firewall corporativo o rechazo del servidor web. No modifica ningun archivo.

Uso:
    python -m scripts.diagnosticar_acceso
"""

from __future__ import annotations

import os
import socket
import ssl
import subprocess
import urllib.error
import urllib.request
from urllib.parse import urlparse

from scripts.configuracion import CKAN_DATASET_API, STABLE_RESOURCES
from scripts.descargar_datos import SOURCE_PAGE, USER_AGENT, _request


HOST = urlparse(SOURCE_PAGE).hostname or "www.datosabiertos.gob.ec"
URLS = {
    "portal": SOURCE_PAGE,
    "api": CKAN_DATASET_API,
    "descarga": STABLE_RESOURCES["actual"]["url"],
}


def _dns() -> tuple[bool, str]:
    try:
        addresses = sorted({info[4][0] for info in socket.getaddrinfo(HOST, 443)})
    except socket.gaierror as exc:
        return False, str(exc)
    return True, ", ".join(addresses)


def _tcp() -> tuple[bool, str]:
    try:
        with socket.create_connection((HOST, 443), timeout=15):
            return True, "puerto 443 abierto"
    except OSError as exc:
        return False, f"{type(exc).__name__}: {exc}"


def _tls() -> tuple[bool, str]:
    try:
        with socket.create_connection((HOST, 443), timeout=15) as raw:
            with ssl.create_default_context().wrap_socket(raw, server_hostname=HOST) as tls:
                issuer = dict(item[0] for item in tls.getpeercert()["issuer"])
                return True, f"{tls.version()}, emisor: {issuer.get('organizationName', '?')}"
    except (OSError, ssl.SSLError) as exc:
        return False, f"{type(exc).__name__}: {exc}"


def _urllib(url: str) -> tuple[int | None, str]:
    request = _request(url)
    request.add_header("Range", "bytes=0-1023")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.headers.get("Content-Type") or ""
    except urllib.error.HTTPError as exc:
        body = exc.read(300).decode("utf-8", errors="replace").strip().replace("\n", " ")
        return exc.code, f"Server: {exc.headers.get('Server') or '?'} | {body[:160]}"
    except (urllib.error.URLError, OSError) as exc:
        return None, str(getattr(exc, "reason", exc))


def _curl(url: str) -> tuple[int | None, str]:
    command = [
        "curl", "--silent", "--show-error", "--location", "--output", "-",
        "--range", "0-1023", "--max-time", "30", "--user-agent", USER_AGENT,
        "--referer", SOURCE_PAGE, "--write-out", "\n%{http_code}", url,
    ]
    try:
        result = subprocess.run(command, capture_output=True, timeout=45)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    code = result.stdout.rsplit(b"\n", 1)[-1].decode(errors="replace").strip()
    if not code.isdigit() or code == "000":
        return None, result.stderr.decode(errors="replace").strip()
    return int(code), ""


def diagnosticar(
    dns: bool,
    tcp: bool,
    tls: bool,
    http: dict[str, dict[str, int | None]],
    proxy: bool = False,
) -> str:
    """Traduce el resultado de cada capa en una causa probable y una accion."""

    codes = [code for result in http.values() for code in result.values()]
    if any(code in (200, 206) for code in http["descarga"].values()):
        return "La descarga funciona desde esta red: ejecute python -m scripts.descargar_datos."
    if 403 in codes:
        return (
            "El servidor responde 403: rechaza esta IP o esta red. Si el navegador si "
            "abre el portal, descargue los dos Excel a mano e importelos con "
            "python -m scripts.descargar_datos --historico ... --actual ...; si tampoco "
            "abre, use otra red o una VPN con salida en Ecuador."
        )
    if proxy and all(code is None for code in codes):
        return (
            "El proxy de esta red (HTTPS_PROXY) no deja pasar al portal: es una politica "
            "de la red, no del portal. Pruebe otra red (hotspot del celular)."
        )
    if not dns:
        return (
            "El dominio no resuelve desde esta red. Puede ser el DNS de la red o "
            "una caida del portal. Pruebe otra red (hotspot del celular) o un DNS publico."
        )
    if not tcp:
        return (
            "La conexion se corta antes de TLS: filtrado por IP o pais en el portal, "
            "o un firewall de la red local. Pruebe otra red (hotspot del celular) "
            "o una VPN con salida en Ecuador."
        )
    if not tls:
        return (
            "Falla el handshake TLS: suele ser un firewall corporativo que intercepta "
            "HTTPS. Pruebe fuera de esa red o sin la VPN institucional."
        )
    return "El servidor no entrega el Excel. Revise los codigos HTTP de arriba."


def main() -> int:
    print(f"Diagnostico de acceso a {HOST}\n")
    dns_ok, dns_detail = _dns()
    print(f"[{'OK' if dns_ok else 'FALLA'}] DNS: {dns_detail}")
    tcp_ok = tls_ok = False
    if dns_ok:
        tcp_ok, tcp_detail = _tcp()
        print(f"[{'OK' if tcp_ok else 'FALLA'}] TCP: {tcp_detail}")
    if tcp_ok:
        tls_ok, tls_detail = _tls()
        print(f"[{'OK' if tls_ok else 'FALLA'}] TLS: {tls_detail}")

    # HTTP se prueba siempre: con un proxy corporativo puede funcionar aunque
    # las pruebas directas de DNS/TCP/TLS fallen.
    http: dict[str, dict[str, int | None]] = {name: {} for name in URLS}
    for name, url in URLS.items():
        for client, probe in (("urllib", _urllib), ("curl", _curl)):
            code, detail = probe(url)
            http[name][client] = code
            print(f"  HTTP {name:<8} {client:<6} -> {code or 'sin respuesta'} {detail}")

    proxy = bool(os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"))
    print(f"\nDiagnostico: {diagnosticar(dns_ok, tcp_ok, tls_ok, http, proxy)}")
    if proxy:
        print("Nota: hay un proxy en HTTPS_PROXY; las pruebas DNS/TCP/TLS no lo usan.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
