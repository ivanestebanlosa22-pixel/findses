"""
make_batch.py — Genera (y opcionalmente sube) VARIOS shorts de una tacada.
==========================================================================

Crea un vídeo por categoría (Verano, Zapatillas, Cazadoras, ...), cada uno con
su descripción y hashtags. Con --upload los manda a tu YouTube tras generarlos.

EJEMPLOS
--------
  # 10 vídeos (uno por categoría), solo generar:
  python3 make_batch.py --limit 10 --count 5

  # con música de fondo:
  python3 make_batch.py --limit 10 --music cancion.mp3

  # generar Y subir a YouTube (privados, para revisar antes):
  python3 make_batch.py --limit 10 --upload --privacy private

Recuerda: esto corre en TU PC (descarga fotos, genera voz y sube con tu sesión).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def slug(text: str) -> str:
    import unicodedata
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_") or "cat"


def pick_categories(catalog: dict, limit: int, min_products: int) -> list[str]:
    por_cat = catalog["meta"].get("por_categoria", {})
    if not por_cat:                                    # fallback: contar
        from collections import Counter
        por_cat = dict(Counter(p["categoria"] for p in catalog["productos"]))
    ordered = sorted(por_cat.items(), key=lambda kv: kv[1], reverse=True)
    return [c for c, n in ordered if n >= min_products][:limit]


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera shorts en lote.")
    ap.add_argument("--catalog", default="catalog.json")
    ap.add_argument("--limit", type=int, default=10, help="nº de vídeos")
    ap.add_argument("--count", type=int, default=5, help="productos por vídeo")
    ap.add_argument("--min-products", type=int, default=20)
    ap.add_argument("--music")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--privacy", default="private",
                    choices=["private", "unlisted", "public"])
    args = ap.parse_args()

    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    cats = pick_categories(catalog, args.limit, args.min_products)
    if not cats:
        print("No hay categorías con suficientes productos.", file=sys.stderr)
        return 1

    print(f"Voy a generar {len(cats)} vídeos: "
          f"{', '.join(cats)}\n")

    import unicodedata
    generated: list[Path] = []
    for i, cat in enumerate(cats, 1):
        clean = unicodedata.normalize("NFKD", cat).encode("ascii", "ignore").decode().strip()
        out_name = f"short_{slug(cat)}.mp4"
        print(f"=== [{i}/{len(cats)}] {clean} -> {out_name} ===")
        cmd = [sys.executable, "make_short.py",
               "--catalog", args.catalog,
               "--category", clean,
               "--count", str(args.count),
               "--output", out_name]
        if args.music:
            cmd += ["--music", args.music]
        if args.demo:
            cmd += ["--demo"]
        r = subprocess.run(cmd)
        if r.returncode == 0:
            generated.append(Path("storage/shorts") / out_name)
        else:
            print(f"  [ERROR] falló la generación de {cat}", file=sys.stderr)
        print()

    print(f"\n[OK] Generados {len(generated)} vídeos en storage/shorts/")

    if args.upload and generated:
        print("\n=== Subiendo a YouTube ===")
        from upload_youtube import get_service, upload_video
        service = get_service()
        for v in generated:
            try:
                upload_video(v, args.privacy, service)
            except Exception as e:
                print(f"  [ERROR] {v.name}: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
