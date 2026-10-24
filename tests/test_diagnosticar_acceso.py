from __future__ import annotations

import unittest

from scripts.diagnosticar_acceso import diagnosticar


def http(code: int | None) -> dict[str, dict[str, int | None]]:
    return {name: {"urllib": code, "curl": code} for name in ("portal", "api", "descarga")}


class DiagnosisTests(unittest.TestCase):
    def test_successful_download_points_to_normal_pipeline(self) -> None:
        result = diagnosticar(True, True, True, http(206))
        self.assertIn("scripts.descargar_datos", result)

    def test_server_403_suggests_manual_import(self) -> None:
        result = diagnosticar(True, True, True, http(403))
        self.assertIn("--historico", result)

    def test_proxy_denial_is_not_blamed_on_the_portal(self) -> None:
        result = diagnosticar(False, False, False, http(None), proxy=True)
        self.assertIn("proxy", result)

    def test_network_layers_are_checked_in_order(self) -> None:
        self.assertIn("no resuelve", diagnosticar(False, False, False, http(None)))
        self.assertIn("antes de TLS", diagnosticar(True, False, False, http(None)))
        self.assertIn("TLS", diagnosticar(True, True, False, http(None)))


if __name__ == "__main__":
    unittest.main()
