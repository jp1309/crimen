from __future__ import annotations

import json
import tempfile
import unittest
import shutil
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook, load_workbook

from scripts.configuracion import STABLE_RESOURCES
from scripts.descargar_datos import (
    SourceUpdateError,
    clasificar_recursos,
    recursos_estables,
    recursos_importados,
    sha256_file,
    sincronizar,
    validar_excel,
)


def resource(name: str, resource_id: str) -> dict[str, object]:
    return {
        "id": resource_id,
        "name": name,
        "format": "XLSX",
        "state": "active",
        "url": f"https://example.invalid/{name}",
    }


class ResourceClassificationTests(unittest.TestCase):
    def test_selects_historical_and_current_accumulated_files(self) -> None:
        resources = [
            resource("mdi_homicidios_intencionales_dd_2025.xlsx", "dictionary"),
            resource("mdi_homicidios_intencionales_pm_2014-2025.xlsx", "historical"),
            resource("mdi_homicidios_intencionales_pm_2026_enero_junio.xlsx", "current"),
        ]

        selected = clasificar_recursos(resources)

        self.assertEqual(selected["historico"]["id"], "historical")
        self.assertEqual(selected["actual"]["id"], "current")

    def test_fails_closed_when_a_primary_source_is_missing(self) -> None:
        with self.assertRaises(SourceUpdateError):
            clasificar_recursos(
                [resource("mdi_homicidios_intencionales_pm_2026_enero_junio.xlsx", "current")]
            )

    def test_stable_resources_preserve_ids_when_api_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "missing-manifest.json"
            selected = recursos_estables(manifest)

        self.assertEqual(selected["historico"]["id"], "36b055c8-e10c-4e57-ba25-3046ca5ef15d")
        self.assertEqual(selected["actual"]["id"], "cb8f704e-2b27-4d7f-9431-d40c4e27fa48")
        self.assertTrue(str(selected["actual"]["url"]).endswith("/download"))


class ExcelValidationTests(unittest.TestCase):
    def test_validates_a_workbook_with_official_headers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.xlsx"
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = "Datos"
            worksheet.append(["PROVINCIA", "CANTON", "FECHA_INFRACCION"])
            for index in range(6_000):
                worksheet.append(["PICHINCHA", "QUITO", f"2026-01-{index % 28 + 1:02d}"])
            workbook.save(path)

            validation = validar_excel(path)

            self.assertEqual(validation["sheet"], "Datos")
            self.assertEqual(validation["header_row"], 1)
            self.assertEqual(len(sha256_file(path)), 64)


class AccumulatedReplacementTests(unittest.TestCase):
    @staticmethod
    def _workbook(path: Path, rows: list[tuple[str, str, str]]) -> None:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.append(["PROVINCIA", "CANTON", "FECHA_INFRACCION"])
        for row in rows:
            worksheet.append(row)
        workbook.save(path)

    def test_current_year_is_replaced_not_appended_and_second_run_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            raw_dir = project / "data" / "raw"
            raw_dir.mkdir(parents=True)
            manifest = project / "data" / "source_manifest.json"
            old_current = raw_dir / "mdi_homicidios_intencionales_pm_actual.xlsx"
            historical = project / "remote-historical.xlsx"
            new_current = project / "remote-current.xlsx"

            self._workbook(
                old_current,
                [("PICHINCHA", "QUITO", "2026-01-01"), ("GUAYAS", "GUAYAQUIL", "2026-02-01")],
            )
            self._workbook(historical, [("PICHINCHA", "QUITO", "2025-01-01")])
            self._workbook(
                new_current,
                [
                    ("PICHINCHA", "QUITO", "2026-01-02"),
                    ("GUAYAS", "GUAYAQUIL", "2026-02-01"),
                    ("AZUAY", "CUENCA", "2026-03-01"),
                ],
            )
            metadata = {
                "id": "dataset",
                "name": "homicidios-intencionales",
                "metadata_modified": "2026-04-15T00:00:00",
                "update_frequency": ["Mensual"],
                "resources": [
                    resource("mdi_homicidios_intencionales_pm_2014-2025.xlsx", "historical"),
                    resource("mdi_homicidios_intencionales_pm_2026_enero_marzo.xlsx", "current"),
                ],
            }
            downloads = {
                STABLE_RESOURCES["historico"]["url"]: historical,
                STABLE_RESOURCES["actual"]["url"]: new_current,
            }

            def fake_download(url: str, destination: Path) -> None:
                shutil.copyfile(downloads[url], destination)

            with (
                patch("scripts.descargar_datos.obtener_metadata", return_value=metadata),
                patch("scripts.descargar_datos.descargar_archivo", side_effect=fake_download),
                patch("scripts.descargar_datos.MIN_XLSX_SIZE", 100),
            ):
                changed, _ = sincronizar(raw_dir=raw_dir, manifest_path=manifest)
                first_manifest_hash = sha256_file(manifest)
                changed_again, _ = sincronizar(raw_dir=raw_dir, manifest_path=manifest)

            workbook = load_workbook(old_current, read_only=True, data_only=True)
            try:
                rows = list(workbook.active.iter_rows(min_row=2, values_only=True))
            finally:
                workbook.close()

            self.assertTrue(changed)
            self.assertFalse(changed_again)
            self.assertEqual(rows, [
                ("PICHINCHA", "QUITO", "2026-01-02"),
                ("GUAYAS", "GUAYAQUIL", "2026-02-01"),
                ("AZUAY", "CUENCA", "2026-03-01"),
            ])
            self.assertEqual(first_manifest_hash, sha256_file(manifest))


class ManualImportTests(unittest.TestCase):
    HISTORICAL = "mdi_homicidiosintencionales_pm_2014_2025.xlsx"
    CURRENT = "mdi_homicidiosintencionales_pm_2026_enero_septiembre.xlsx"

    def test_rejects_dictionary_swapped_or_incomplete_sources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for name in (self.HISTORICAL, self.CURRENT, "mdi_homicidios_intencionales_dd_2026.xlsx"):
                (folder / name).write_bytes(b"x")
            manifest = folder / "missing-manifest.json"

            cases = [
                {"historico": folder / self.HISTORICAL},
                {"historico": folder / self.CURRENT, "actual": folder / self.HISTORICAL},
                {
                    "historico": folder / self.HISTORICAL,
                    "actual": folder / "mdi_homicidios_intencionales_dd_2026.xlsx",
                },
                {"historico": folder / self.HISTORICAL, "actual": folder / "no-existe.xlsx"},
            ]
            for archivos in cases:
                with self.subTest(archivos=archivos), self.assertRaises(SourceUpdateError):
                    recursos_importados(archivos, manifest)

    def test_imports_without_network_and_second_run_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            raw_dir = project / "data" / "raw"
            manifest = project / "data" / "source_manifest.json"
            archivos = {
                "historico": project / self.HISTORICAL,
                "actual": project / self.CURRENT,
            }
            AccumulatedReplacementTests._workbook(
                archivos["historico"], [("PICHINCHA", "QUITO", "2025-01-01")]
            )
            AccumulatedReplacementTests._workbook(
                archivos["actual"], [("GUAYAS", "GUAYAQUIL", "2026-09-01")]
            )

            with (
                patch("scripts.descargar_datos.obtener_metadata", side_effect=AssertionError),
                patch("scripts.descargar_datos.descargar_archivo", side_effect=AssertionError),
                patch("scripts.descargar_datos.MIN_XLSX_SIZE", 100),
            ):
                changed, _ = sincronizar(
                    raw_dir=raw_dir, manifest_path=manifest, archivos_locales=archivos
                )
                changed_again, _ = sincronizar(
                    raw_dir=raw_dir, manifest_path=manifest, archivos_locales=archivos
                )

            resources = json.loads(manifest.read_text(encoding="utf-8"))["resources"]
            self.assertTrue(changed)
            self.assertFalse(changed_again)
            self.assertEqual(resources["actual"]["origin"], "importacion_manual")
            self.assertEqual(resources["actual"]["official_name"], self.CURRENT)
            self.assertEqual(
                resources["actual"]["resource_id"], STABLE_RESOURCES["actual"]["id"]
            )
            self.assertEqual(
                sha256_file(raw_dir / "mdi_homicidios_intencionales_pm_actual.xlsx"),
                sha256_file(archivos["actual"]),
            )


if __name__ == "__main__":
    unittest.main()
