"""
make_short.py — FindsES
=======================
Genera un VÍDEO CORTO VERTICAL (1080x1920, 9:16) tipo "finds" a partir de los
productos de `catalog.json`:

    [Gancho]  ->  [Producto 1]  ->  [Producto 2]  -> ...  ->  [Cierre + Discord]

Cada producto muestra: tu FOTO QC real a pantalla completa, el NOMBRE arriba,
el PRECIO en € en un badge grande, y un SUBTÍTULO quemado sincronizado con la
narración (voz femenina edge-tts).

REGLA DE MARCA (innegociable): solo afirmaciones verdaderas. Nada de "miles de
miembros" ni ventas inventadas. Usamos: +3.000 productos, precios en €, QC real,
100% español.

--------------------------------------------------------------------------------
MODOS
--------------------------------------------------------------------------------
  Real (en tu PC, con internet):
      python3 make_short.py --category "Verano" --count 5
      -> descarga las fotos, genera voz, y produce el .mp4 final

  Demo (sin internet, p. ej. en este entorno cloud):
      python3 make_short.py --category "Verano" --count 5 --demo
      -> usa imágenes placeholder y audio silencioso (valida el motor de render)

Requisitos (instalables con pip):  Pillow  imageio-ffmpeg  edge-tts
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

import imageio_ffmpeg

# --------------------------------------------------------------------------- #
# Configuración general
# --------------------------------------------------------------------------- #
WIDTH, HEIGHT = 1080, 1920          # formato vertical 9:16
FPS = 30
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

OUT_DIR = Path("storage/shorts")
TMP_DIR = Path("storage/tmp")

VOICE = "es-ES-ElviraNeural"        # voz femenina española
HOOK_SECONDS = 1.6                  # duración del gancho
OUTRO_SECONDS = 2.6                 # duración del cierre
DEMO_PRODUCT_SECONDS = 2.8          # duración por producto en modo demo (sin voz)

# Afirmaciones VERDADERAS para el cierre (regla de honestidad).
CLAIM_LINE_1 = "+3.000 productos · QC real"
CLAIM_LINE_2 = "100% español"

# Paleta
BG_DARK = (16, 16, 22)
ACCENT = (255, 70, 85)              # rojo FindsES para el badge de precio
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# --------------------------------------------------------------------------- #
# Fuentes (usamos las del sistema; Liberation Sans Bold ≈ Arial Bold)
# --------------------------------------------------------------------------- #
def _find_font(bold: bool = True) -> str:
    candidates = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return ""  # Pillow caerá a la fuente por defecto


FONT_PATH = _find_font()


def font(size: int) -> ImageFont.FreeTypeFont:
    if FONT_PATH:
        return ImageFont.truetype(FONT_PATH, size)
    return ImageFont.load_default()


# --------------------------------------------------------------------------- #
# Utilidades de texto
# --------------------------------------------------------------------------- #
def strip_emoji(text: str) -> str:
    """Quita emojis y símbolos: las fuentes del sistema no los dibujan bien."""
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat in ("So", "Sk", "Cs") or ord(ch) > 0x2700:
            continue
        out.append(ch)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def wrap(draw, text, fnt, max_w):
    """Parte el texto en líneas que quepan en max_w píxeles."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, lines, fnt, y, fill=WHITE, stroke=4, stroke_fill=BLACK,
                  line_gap=12):
    """Dibuja líneas centradas horizontalmente con borde (alto contraste)."""
    for line in lines:
        w = draw.textlength(line, font=fnt)
        x = (WIDTH - w) // 2
        draw.text((x, y), line, font=fnt, fill=fill,
                  stroke_width=stroke, stroke_fill=stroke_fill)
        ascent, descent = fnt.getmetrics()
        y += ascent + descent + line_gap
    return y


def price_str(value: float) -> str:
    """38.0 -> '38€' ; 38.5 -> '38,50€' (formato español)."""
    if float(value).is_integer():
        return f"{int(value)}€"
    return f"{value:.2f}".replace(".", ",") + "€"


# --------------------------------------------------------------------------- #
# Construcción de los fotogramas (cada "tarjeta" es un PNG de 1080x1920)
# --------------------------------------------------------------------------- #
def card_hook(text: str) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    d = ImageDraw.Draw(img)
    fnt = font(96)
    lines = wrap(d, text.upper(), fnt, WIDTH - 160)
    total_h = len(lines) * (sum(fnt.getmetrics()) + 12)
    draw_centered(d, lines, fnt, (HEIGHT - total_h) // 2, fill=WHITE, stroke=6)
    # marca
    fb = font(48)
    draw_centered(d, ["FindsES"], fb, HEIGHT - 220, fill=ACCENT, stroke=4)
    return img


def _fit_cover(src: Image.Image, w: int, h: int) -> Image.Image:
    """Escala recortando para cubrir w×h (sin deformar)."""
    sr, tr = src.width / src.height, w / h
    if sr > tr:
        nh = h
        nw = int(h * sr)
    else:
        nw = w
        nh = int(w / sr)
    src = src.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return src.crop((left, top, left + w, top + h))


# Regiones verticales fijas del layout de producto (evitan solapamientos).
TITLE_Y = 120          # nombre (arriba)
PHOTO_BOX = 800        # lado del cuadro de la foto
PHOTO_TOP = 360        # borde superior de la foto  -> abajo en 1160
BADGE_TOP = 1230       # badge de precio
CAPTION_Y = 1560       # caption corto (parte inferior)


def card_product(photo: Image.Image, name: str, price: float,
                 caption: str) -> Image.Image:
    """Tarjeta de producto: fondo difuminado + foto + nombre arriba + precio + caption corto.

    Cada elemento vive en su banda vertical para que nunca se solapen.
    """
    photo = photo.convert("RGB")

    # Fondo: la propia foto, ampliada para cubrir, difuminada y oscurecida.
    bg = _fit_cover(photo, WIDTH, HEIGHT).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (WIDTH, HEIGHT), BLACK), 0.45)
    img = bg

    # Foto nítida centrada en su banda.
    fg = _fit_cover(photo, PHOTO_BOX, PHOTO_BOX)
    img.paste(fg, ((WIDTH - PHOTO_BOX) // 2, PHOTO_TOP))

    d = ImageDraw.Draw(img)

    # Nombre (banda superior, máx 2 líneas).
    fnt_name = font(60)
    name_lines = wrap(d, strip_emoji(name), fnt_name, WIDTH - 160)[:2]
    draw_centered(d, name_lines, fnt_name, TITLE_Y, fill=WHITE, stroke=5)

    # Badge de precio (banda propia, debajo de la foto).
    pstr = price_str(price)
    fnt_price = font(104)
    pw = d.textlength(pstr, font=fnt_price)
    ph = sum(fnt_price.getmetrics())
    pad_x, pad_y = 48, 20
    bx0 = (WIDTH - pw) // 2 - pad_x
    bx1 = bx0 + pw + 2 * pad_x
    by1 = BADGE_TOP + ph + 2 * pad_y
    d.rounded_rectangle([bx0, BADGE_TOP, bx1, by1], radius=36, fill=ACCENT)
    d.text(((WIDTH - pw) // 2, BADGE_TOP + pad_y), pstr, font=fnt_price,
           fill=WHITE, stroke_width=3, stroke_fill=BLACK)

    # Caption corto (banda inferior, ≤ ~6 palabras, no duplica nombre ni precio).
    if caption:
        fnt_cap = font(56)
        cap_lines = wrap(d, strip_emoji(caption).upper(), fnt_cap, WIDTH - 140)
        draw_centered(d, cap_lines, fnt_cap, CAPTION_Y, fill=WHITE, stroke=5)
    return img


def card_outro(discord: str | None) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    d = ImageDraw.Draw(img)
    y = HEIGHT // 2 - 320
    y = draw_centered(d, [CLAIM_LINE_1], font(64), y, fill=WHITE, stroke=5)
    y = draw_centered(d, [CLAIM_LINE_2], font(64), y + 10, fill=WHITE, stroke=5)
    draw_centered(d, ["ÚNETE AL DISCORD"], font(86), y + 80, fill=ACCENT, stroke=6)
    if discord:
        link = discord.replace("https://", "")
        draw_centered(d, [link], font(48), y + 230, fill=WHITE, stroke=4)
    return img


# --------------------------------------------------------------------------- #
# Fotos y voz (red real) con degradación elegante en modo demo
# --------------------------------------------------------------------------- #
def download_photo(url: str) -> Image.Image:
    """Descarga una foto de producto. Requiere internet (no funciona en el sandbox)."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
        "Referer": "https://weidian.com/",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    return Image.open(_bytes_io(data))


def placeholder_photo(name: str, idx: int) -> Image.Image:
    """Imagen de relleno para el modo demo (sin red)."""
    colors = [(40, 50, 80), (80, 40, 60), (40, 70, 60), (70, 60, 40), (55, 45, 75)]
    img = Image.new("RGB", (900, 900), colors[idx % len(colors)])
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 40, 860, 860], radius=30, outline=(255, 255, 255), width=6)
    lines = wrap(d, strip_emoji(name) or "PRODUCTO", font(54), 760)
    draw_centered_box(d, lines, font(54), 900, 900)
    return img


def draw_centered_box(d, lines, fnt, w, h):
    total = len(lines) * (sum(fnt.getmetrics()) + 10)
    y = (h - total) // 2
    for line in lines:
        tw = d.textlength(line, font=fnt)
        d.text(((w - tw) // 2, y), line, font=fnt, fill=(255, 255, 255),
               stroke_width=3, stroke_fill=(0, 0, 0))
        y += sum(fnt.getmetrics()) + 10


def _bytes_io(data: bytes):
    import io
    return io.BytesIO(data)


def narration_for(product: dict) -> str:
    """Texto honesto que se narrará para un producto."""
    name = strip_emoji(product["producto"])
    return f"{name}. {price_str(product['precio_eur'])}, con QC real."


async def synth_voice(text: str, out_path: Path) -> None:
    """Genera la voz con edge-tts (requiere internet)."""
    import edge_tts
    await edge_tts.Communicate(text, VOICE).save(str(out_path))


def audio_duration(path: Path) -> float:
    """Duración de un audio en segundos usando ffmpeg."""
    out = subprocess.run(
        [FFMPEG, "-i", str(path), "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    m = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", out[::-1][:200][::-1]) or \
        re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    if not m:
        return 3.0
    h, mn, s = m.groups()
    return int(h) * 3600 + int(mn) * 60 + float(s)


# --------------------------------------------------------------------------- #
# Composición final con ffmpeg
# --------------------------------------------------------------------------- #
def build_video(segments: list[dict], out_path: Path, music: Path | None) -> None:
    """
    segments: lista de {image: Path, audio: Path|None, duration: float}
    Crea un clip por segmento (imagen fija + su audio) y los concatena.
    """
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, seg in enumerate(segments):
        part = TMP_DIR / f"part_{i:03d}.mp4"
        dur = seg["duration"]
        cmd = [FFMPEG, "-y", "-loop", "1", "-i", str(seg["image"])]
        if seg["audio"]:
            cmd += ["-i", str(seg["audio"])]
        else:
            # pista de silencio para que todos los clips tengan audio (concat uniforme)
            cmd += ["-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo"]
        cmd += [
            "-t", f"{dur:.3f}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-vf", f"scale={WIDTH}:{HEIGHT},format=yuv420p",
            # Normalizamos TODO el audio a 44100 Hz estéreo. Si no, los clips de
            # voz (24000 Hz de edge-tts) y los de silencio (44100 Hz) tienen
            # frecuencias distintas y, al concatenar, la voz suena acelerada
            # y aguda (efecto "cámara rápida" / ardilla).
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-shortest", str(part),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        parts.append(part)

    # Lista para el demuxer concat.
    # OJO Windows: el demuxer concat trata '\' como escape, así que las rutas
    # deben ir con barras normales '/' (as_posix), o ffmpeg falla con EINVAL.
    listfile = TMP_DIR / "concat.txt"
    listfile.write_text(
        "".join(f"file '{p.resolve().as_posix()}'\n" for p in parts)
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    concat_cmd = [
        FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
    ]
    if music and music.exists():
        # Mezcla música de fondo a bajo volumen bajo la narración.
        concat_cmd += ["-stream_loop", "-1", "-i", str(music),
                       "-filter_complex",
                       "[1:a]volume=0.18[m];[0:a][m]amix=inputs=2:duration=first[a]",
                       "-map", "0:v", "-map", "[a]"]
    concat_cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p",
                   "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                   str(out_path)]
    subprocess.run(concat_cmd, check=True, capture_output=True)


# --------------------------------------------------------------------------- #
# Orquestación
# --------------------------------------------------------------------------- #
def pick_products(catalog: dict, category: str | None, count: int) -> list[dict]:
    prods = catalog["productos"]
    if category:
        cat_l = category.lower()
        prods = [p for p in prods
                 if cat_l in strip_emoji(p["categoria"]).lower()]
    prods = [p for p in prods if p["fotos"]]  # solo con foto
    return prods[:count]


async def run(args) -> int:
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    discord = catalog["meta"].get("discord")
    products = pick_products(catalog, args.category, args.count)
    if not products:
        print("No hay productos que cumplan el filtro.", file=sys.stderr)
        return 1

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    cat_label = strip_emoji(products[0]["categoria"]).upper()
    hook_text = args.hook or f"{len(products)} FINDS DE {cat_label}"

    segments: list[dict] = []

    # 1) Gancho
    hook_img = TMP_DIR / "card_hook.png"
    card_hook(hook_text).save(hook_img)
    segments.append({"image": hook_img, "audio": None, "duration": HOOK_SECONDS})

    # 2) Productos
    print(f"Generando {len(products)} tarjetas de producto"
          f"{' (DEMO)' if args.demo else ''}...")
    for i, p in enumerate(products):
        # Foto
        if args.demo:
            photo = placeholder_photo(p["producto"], i)
        else:
            try:
                photo = download_photo(p["fotos"][0])
            except Exception as e:
                print(f"  Foto falló ({e}); uso placeholder.", file=sys.stderr)
                photo = placeholder_photo(p["producto"], i)

        # Voz / duración
        narration = narration_for(p)
        if args.demo:
            audio = None
            duration = DEMO_PRODUCT_SECONDS
        else:
            audio = TMP_DIR / f"voice_{i:03d}.mp3"
            try:
                await synth_voice(narration, audio)
                duration = audio_duration(audio) + 0.4
            except Exception as e:
                print(f"  Voz falló ({e}); sin audio.", file=sys.stderr)
                audio, duration = None, DEMO_PRODUCT_SECONDS

        # El caption en pantalla es corto y honesto (no duplica nombre/precio);
        # la narración completa va en el audio.
        card = card_product(photo, p["producto"], p["precio_eur"],
                            caption="QC real verificado")
        img_path = TMP_DIR / f"card_prod_{i:03d}.png"
        card.save(img_path)
        segments.append({"image": img_path, "audio": audio, "duration": duration})
        print(f"  [{i+1}/{len(products)}] {strip_emoji(p['producto'])} "
              f"— {price_str(p['precio_eur'])} ({duration:.1f}s)")

    # 3) Cierre
    outro_img = TMP_DIR / "card_outro.png"
    card_outro(discord).save(outro_img)
    segments.append({"image": outro_img, "audio": None, "duration": OUTRO_SECONDS})

    # 4) Render
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / args.output
    music = Path(args.music) if args.music else None
    print("Renderizando con ffmpeg...")
    build_video(segments, out, music)

    total = sum(s["duration"] for s in segments)
    size_mb = out.stat().st_size / 1_000_000
    print(f"\n[OK] Vídeo generado: {out}")
    print(f"     Duración ~{total:.1f}s · {WIDTH}x{HEIGHT} · {size_mb:.1f} MB")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera un short vertical de FindsES.")
    ap.add_argument("--catalog", default="catalog.json")
    ap.add_argument("--category", help="Filtra por categoría (ej. 'Verano').")
    ap.add_argument("--count", type=int, default=5, help="Nº de productos.")
    ap.add_argument("--hook", help="Texto del gancho (opcional).")
    ap.add_argument("--music", help="Ruta a música de fondo (opcional).")
    ap.add_argument("--output", default="short.mp4")
    ap.add_argument("--demo", action="store_true",
                    help="Sin red: placeholders + audio silencioso.")
    args = ap.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
