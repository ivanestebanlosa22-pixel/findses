"""
extract_catalog.py — FindsES
=============================
Lee la spreadsheet (.xlsx) del catálogo FindsES y genera un `catalog.json`
limpio y fácil de consumir por el resto del pipeline de vídeos.

Por cada producto extrae:
  - categoria        (la pestaña: Verano, Zapatillas, ...)
  - producto         (nombre, sin el ✅ inicial)
  - tienda           (vendedor, si aparece)
  - precio_eur       (float)
  - fotos            (lista de URLs de las fórmulas =IMAGE("..."))
  - qc               (link al QC, de =HYPERLINK("..."))
  - usfans/litbuy/kakobuy  (links de compra con tus códigos de afiliado)

Decisiones de diseño:
  - Usamos SOLO la librería estándar (zipfile + xml). Motivo: un .xlsx es un
    ZIP con XML dentro; openpyxl no expone bien las fórmulas =IMAGE(), así que
    parseamos el XML a mano. Cero dependencias = corre en cualquier máquina.
  - Es de SOLO LECTURA: nunca modifica el .xlsx original.

Uso:
    python3 extract_catalog.py                # autodetecta el .xlsx del repo
    python3 extract_catalog.py archivo.xlsx   # ruta explícita
"""

from __future__ import annotations

import glob
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Namespace del formato OOXML (SpreadsheetML). Todas las etiquetas lo llevan.
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

# Mapa fijo de columnas de cada pestaña de categoría (verificado en la hoja):
#   A,B,C = 📸 FOTO 1/2/3 (=IMAGE)   D = 🏷️ PRODUCTO   E = 🏪 TIENDA
#   F = 💶 €             G = 📸 QC (=HYPERLINK)
#   H = 🟠 USFANS  I = 🟡 LITBUY  J = 🔴 KAKOBUY  (todos =HYPERLINK)
COL = {
    "foto1": "A", "foto2": "B", "foto3": "C",
    "producto": "D", "tienda": "E", "precio": "F", "qc": "G",
    "usfans": "H", "litbuy": "I", "kakobuy": "J",
}

# Pestañas que NO son catálogo de productos (portada, índice...).
SKIP_SHEETS = {"🏠 INICIO"}


def _col_letter(cell_ref: str) -> str:
    """De 'B12' devuelve 'B' (la letra de columna)."""
    return re.match(r"[A-Z]+", cell_ref).group()


def _strip_tags(xml_fragment: str) -> str:
    """Quita etiquetas XML y los bloques de fonética (rPh) de un <si>."""
    no_phonetic = re.sub(r"<rPh.*?</rPh>", "", xml_fragment, flags=re.S)
    return re.sub(r"<[^>]+>", "", no_phonetic).strip()


def _load_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    """Carga la tabla de cadenas compartidas (sharedStrings.xml)."""
    try:
        raw = zf.read("xl/sharedStrings.xml").decode("utf-8", "ignore")
    except KeyError:
        return []
    return [_strip_tags(si) for si in re.findall(r"<si>(.*?)</si>", raw, re.S)]


def _sheet_names(zf: zipfile.ZipFile) -> list[str]:
    """Nombres de las pestañas, en orden (coinciden con sheet1.xml, sheet2.xml...)."""
    wb = zf.read("xl/workbook.xml").decode("utf-8", "ignore")
    return re.findall(r'<sheet[^>]*name="([^"]+)"', wb)


def _first_url(formula: str | None) -> str | None:
    """Extrae la primera URL de una fórmula =IMAGE("url") o =HYPERLINK("url",...)."""
    if not formula:
        return None
    m = re.search(r'https?://[^"\)]+', formula)
    return m.group() if m else None


def _cell_value(cell: ET.Element, shared: list[str]):
    """Devuelve el valor 'útil' de una celda: texto de fórmula, string o número."""
    cell_type = cell.get("t")
    formula = cell.find(f"{NS}f")
    value = cell.find(f"{NS}v")
    if formula is not None and formula.text:
        return formula.text                      # fórmula cruda (=IMAGE/HYPERLINK)
    if value is not None and value.text is not None:
        if cell_type == "s":                     # índice a sharedStrings
            idx = int(value.text)
            return shared[idx] if idx < len(shared) else ""
        return value.text                        # número o valor directo
    return None


def _clean_name(raw: str) -> str:
    """Limpia el nombre del producto: quita el ✅ inicial y espacios sobrantes."""
    return re.sub(r"^[✅\s]+", "", raw).strip()


def extract(xlsx_path: Path) -> dict:
    """Procesa el .xlsx completo y devuelve el catálogo como dict."""
    zf = zipfile.ZipFile(xlsx_path)
    shared = _load_shared_strings(zf)
    names = _sheet_names(zf)

    # Ordenamos los worksheets por su número (sheet1, sheet2, ...) para que el
    # índice coincida con el nombre de pestaña correspondiente.
    sheet_files = sorted(
        (n for n in zf.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml", n)),
        key=lambda n: int(re.search(r"\d+", n.split("/")[-1]).group()),
    )

    products: list[dict] = []
    discord = None
    by_category: dict[str, int] = {}

    for idx, sheet_file in enumerate(sheet_files):
        category = names[idx] if idx < len(names) else sheet_file
        root = ET.fromstring(zf.read(sheet_file).decode("utf-8", "ignore"))

        for row in root.iter(f"{NS}row"):
            cells = {
                _col_letter(c.get("r")): _cell_value(c, shared)
                for c in row.iter(f"{NS}c")
                if c.get("r")
            }

            # Capturamos el enlace de Discord allá donde aparezca (suele estar
            # en una celda de cabecera con =HYPERLINK("https://discord.gg/...")).
            for val in cells.values():
                if isinstance(val, str) and "discord.gg" in val and discord is None:
                    discord = _first_url(val)

            if category in SKIP_SHEETS:
                continue

            name = cells.get(COL["producto"])
            price = cells.get(COL["precio"])

            # Una fila es un producto válido si tiene nombre y precio numérico.
            if not (isinstance(name, str) and name.strip()):
                continue
            if not (isinstance(price, str) and re.match(r"^\d+\.?\d*$", price)):
                continue

            fotos = [
                _first_url(cells.get(COL[k]))
                for k in ("foto1", "foto2", "foto3")
            ]
            fotos = [f for f in fotos if f]  # quitamos las vacías

            products.append({
                "categoria": category,
                "producto": _clean_name(name),
                "tienda": cells.get(COL["tienda"]) or None,
                "precio_eur": round(float(price), 2),
                "fotos": fotos,
                "qc": _first_url(cells.get(COL["qc"])),
                "usfans": _first_url(cells.get(COL["usfans"])),
                "litbuy": _first_url(cells.get(COL["litbuy"])),
                "kakobuy": _first_url(cells.get(COL["kakobuy"])),
            })
            by_category[category] = by_category.get(category, 0) + 1

    return {
        "meta": {
            "fuente": xlsx_path.name,
            "total_productos": len(products),
            "por_categoria": by_category,
            "discord": discord,
        },
        "productos": products,
    }


def main() -> int:
    # Localizamos el .xlsx: argumento explícito o autodetección en el repo.
    if len(sys.argv) > 1:
        xlsx_path = Path(sys.argv[1])
    else:
        matches = glob.glob("*.xlsx")
        if not matches:
            print("ERROR: no encuentro ningún .xlsx en esta carpeta.", file=sys.stderr)
            return 1
        xlsx_path = Path(matches[0])

    if not xlsx_path.exists():
        print(f"ERROR: no existe el archivo {xlsx_path}", file=sys.stderr)
        return 1

    print(f"Leyendo: {xlsx_path.name}")
    catalog = extract(xlsx_path)

    out = Path("catalog.json")
    out.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    meta = catalog["meta"]
    print(f"\n[OK] Generado {out} con {meta['total_productos']} productos.")
    print(f"     Discord detectado: {meta['discord']}")
    print("     Productos por categoría:")
    for cat, n in meta["por_categoria"].items():
        print(f"       - {cat}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
