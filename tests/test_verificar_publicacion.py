from __future__ import annotations

import unittest

from scripts.verificar_publicacion import comparar_csv, normalizar_saltos


class PublicationVerificationTests(unittest.TestCase):
    def test_accepts_only_line_ending_normalization(self) -> None:
        local = b"fecha_infraccion,valor\r\n2026-07-31,1\r\n"
        public = b"fecha_infraccion,valor\n2026-07-31,1\n"

        result = comparar_csv(local, public)

        self.assertEqual(result["rows"], 1)
        self.assertEqual(result["max_date"], "2026-07-31")
        self.assertEqual(normalizar_saltos(local), public)

    def test_rejects_semantic_differences(self) -> None:
        local = b"fecha_infraccion,valor\n2026-07-31,1\n"
        public = b"fecha_infraccion,valor\n2026-07-31,2\n"

        with self.assertRaises(ValueError):
            comparar_csv(local, public)


if __name__ == "__main__":
    unittest.main()
