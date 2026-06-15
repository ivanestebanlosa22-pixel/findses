"""
make_short.py — FindsES (motor v2, "pro")
==========================================
Genera un SHORT vertical (1080x1920, 9:16) de nivel profesional a partir de
`catalog.json`:

    [Gancho]  ->  [Producto x N]  ->  [Cierre + Discord]

Mejoras v2 frente a la versión estática:
  - Render FOTOGRAMA A FOTOGRAMA (Pillow) -> control total de animación.
  - Movimiento "Ken Burns" (zoom/paneo lento) sobre cada foto.
  - Precio que entra con animación de rebote (pop).
  - SUBTÍTULOS KARAOKE palabra a palabra, sincronizados con la voz real.
  - Música de fondo mezclada por debajo de la voz.
  - Voz: ElevenLabs (casi humana, recomendado) con fallback a edge-tts.

REGLA DE MARCA (innegociable): solo datos verdaderos. Nada inventado.
Usamos: +3.000 productos, precios en €, QC real, 100% español.

--------------------------------------------------------------------------------
CONFIGURACIÓN DE VOZ
--------------------------------------------------------------------------------
Crea un archivo `.env` (NO se sube a git) con:

    ELEVENLABS_API_KEY=sk_xxxxxxxx
    ELEVENLABS_VOICE_ID=XXXXXXXXXXXXXXXX        # voz española que elijas
    ELEVENLABS_MODEL=eleven_multilingual_v2

Sin API key -> usa edge-tts (gratis, voz robótica) automáticamente.

--------------------------------------------------------------------------------
USO
--------------------------------------------------------------------------------
  Real (tu PC, con internet):
      python3 make_short.py --category "Verano" --count 5 --music cancion.mp3
  Demo (sin red, valida el motor visual):
      python3 make_short.py --category "Verano" --count 5 --demo

Requisitos:  pip install Pillow imageio-ffmpeg edge-tts
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import math
import os
import re
import subprocess
import sys
import unicodedata
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

import imageio_ffmpeg

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
WIDTH, HEIGHT = 1080, 1920
FPS = 30
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

OUT_DIR = Path("storage/shorts")
TMP_DIR = Path("storage/tmp")

HOOK_SECONDS = 1.8
OUTRO_SECONDS = 3.0
DEMO_PRODUCT_SECONDS = 3.2          # duración por producto en demo (sin voz)
TAIL_SILENCE = 0.5                  # cola de silencio tras cada narración

CLAIM_LINE_1 = "+3.000 productos · QC real"
CLAIM_LINE_2 = "100% español 🇪🇸"

# Paleta
BG = (14, 14, 20)
ACCENT = (255, 60, 78)
WHITE = (255, 255, 255)
YELLOW = (255, 214, 10)             # palabra activa del karaoke
BLACK = (0, 0, 0)


# --------------------------------------------------------------------------- #
# .env loader minimalista (sin dependencias)
# --------------------------------------------------------------------------- #
def load_env(path: str = ".env") -> None:
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


# --------------------------------------------------------------------------- #
# Fuentes
# --------------------------------------------------------------------------- #
def _find_font(bold: bool) -> str:
    names = (
        ["LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf", "arialbd.ttf"]
        if bold else
        ["LiberationSans-Regular.ttf", "DejaVuSans.ttf", "arial.ttf"]
    )
    dirs = [
        "/usr/share/fonts/truetype/liberation/",
        "/usr/share/fonts/truetype/dejavu/",
        "C:/Windows/Fonts/",
    ]
    for d in dirs:
        for n in names:
            if Path(d + n).exists():
                return d + n
    return ""


FONT_BOLD = _find_font(bold=True)


def font(size: int) -> ImageFont.FreeTypeFont:
    if FONT_BOLD:
        return ImageFont.truetype(FONT_BOLD, size)
    return ImageFont.load_default()


# --------------------------------------------------------------------------- #
# Utilidades de texto
# --------------------------------------------------------------------------- #
def strip_emoji(text: str) -> str:
    out = []
    for ch in text:
        if unicodedata.category(ch) in ("So", "Sk", "Cs") or ord(ch) > 0x2600:
            continue
        out.append(ch)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def wrap(draw, text, fnt, max_w):
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


def price_str(value: float) -> str:
    if float(value).is_integer():
        return f"{int(value)}€"
    return f"{value:.2f}".replace(".", ",") + "€"


# --------------------------------------------------------------------------- #
# Easing (curvas de animación)
# --------------------------------------------------------------------------- #
def smooth(p: float) -> float:
    p = max(0.0, min(1.0, p))
    return p * p * (3 - 2 * p)


def back_out(p: float) -> float:
    """Rebote suave al final (para el 'pop' del precio)."""
    p = max(0.0, min(1.0, p))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2


# --------------------------------------------------------------------------- #
# Imagen: cover-fit
# --------------------------------------------------------------------------- #
def fit_cover(src: Image.Image, w: int, h: int) -> Image.Image:
    sr, tr = src.width / src.height, w / h
    if sr > tr:
        nw, nh = int(h * sr), h
    else:
        nw, nh = w, int(w / sr)
    src = src.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return src.crop((left, top, left + w, top + h))


# --------------------------------------------------------------------------- #
# Texto con borde (alto contraste)
# --------------------------------------------------------------------------- #
def text_centered(draw, text, fnt, y, fill=WHITE, stroke=6, sfill=BLACK):
    w = draw.textlength(text, font=fnt)
    draw.text(((WIDTH - w) // 2, y), text, font=fnt, fill=fill,
              stroke_width=stroke, stroke_fill=sfill)


# --------------------------------------------------------------------------- #
# VOZ — devuelve (audio_path|None, word_timings, duration)
#   word_timings: lista de (palabra, t_inicio, t_fin) en segundos
# --------------------------------------------------------------------------- #
def get_voice(text: str, idx: int, demo: bool) -> tuple[Path | None, list, float]:
    if demo:
        return _fake_timings(text, DEMO_PRODUCT_SECONDS)

    out = TMP_DIR / f"voice_{idx:03d}.mp3"
    api = os.environ.get("ELEVENLABS_API_KEY")
    if api:
        try:
            return _elevenlabs(text, out, api)
        except Exception as e:
            print(f"  ElevenLabs falló ({e}); uso edge-tts.", file=sys.stderr)
    try:
        return _edge(text, out)
    except Exception as e:
        print(f"  Voz falló ({e}); sigo sin audio.", file=sys.stderr)
        return _fake_timings(text, DEMO_PRODUCT_SECONDS)


def _fake_timings(text: str, dur: float):
    """Sin audio: reparte las palabras de forma uniforme (para demo)."""
    words = strip_emoji(text).split()
    if not words:
        return None, [], dur
    span = dur - 0.4
    step = span / len(words)
    timings = [(w, 0.2 + i * step, 0.2 + (i + 1) * step)
               for i, w in enumerate(words)]
    return None, timings, dur


def _edge(text: str, out: Path):
    """edge-tts con marcas de palabra (WordBoundary) para el karaoke."""
    import edge_tts
    voice = os.environ.get("EDGE_VOICE", "es-ES-ElviraNeural")

    async def go():
        comm = edge_tts.Communicate(text, voice)
        timings, audio = [], b""
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio += chunk["data"]
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 1e7          # 100ns -> s
                end = start + chunk["duration"] / 1e7
                timings.append((chunk["text"], start, end))
        out.write_bytes(audio)
        return timings

    timings = asyncio.get_event_loop().run_until_complete(go()) \
        if asyncio.get_event_loop().is_running() else asyncio.run(go())
    dur = (timings[-1][2] if timings else 3.0) + TAIL_SILENCE
    return out, timings, dur


def _elevenlabs(text: str, out: Path, api_key: str):
    """ElevenLabs con timestamps por carácter -> los agrupo en palabras."""
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID")
    if not voice_id:
        raise RuntimeError("Falta ELEVENLABS_VOICE_ID en .env")
    model = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
    body = json.dumps({
        "text": text,
        "model_id": model,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())

    out.write_bytes(base64.b64decode(data["audio_base64"]))

    al = data.get("alignment") or {}
    chars = al.get("characters", [])
    starts = al.get("character_start_times_seconds", [])
    ends = al.get("character_end_times_seconds", [])

    # Reconstruimos palabras a partir de los caracteres y sus tiempos.
    timings, cur, c_start, c_end = [], "", None, None
    for ch, s, e in zip(chars, starts, ends):
        if ch.isspace():
            if cur:
                timings.append((cur, c_start, c_end))
                cur, c_start = "", None
        else:
            if c_start is None:
                c_start = s
            cur += ch
            c_end = e
    if cur:
        timings.append((cur, c_start, c_end))

    dur = (ends[-1] if ends else 3.0) + TAIL_SILENCE
    return out, timings, dur


# --------------------------------------------------------------------------- #
# Fotos
# --------------------------------------------------------------------------- #
def download_photo(url: str) -> Image.Image:
    import io
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
        "Referer": "https://weidian.com/",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


def placeholder_photo(name: str, idx: int) -> Image.Image:
    colors = [(40, 50, 80), (80, 40, 60), (40, 70, 60), (70, 60, 40), (55, 45, 75)]
    img = Image.new("RGB", (1000, 1000), colors[idx % len(colors)])
    d = ImageDraw.Draw(img)
    fnt = font(54)
    lines = wrap(d, strip_emoji(name) or "PRODUCTO", fnt, 860)
    y = 500 - len(lines) * 40
    for ln in lines:
        text_centered_box(d, ln, fnt, y, 1000)
        y += 80
    return img


def text_centered_box(d, text, fnt, y, w):
    tw = d.textlength(text, font=fnt)
    d.text(((w - tw) // 2, y), text, font=fnt, fill=WHITE, stroke_width=3,
           stroke_fill=BLACK)


# --------------------------------------------------------------------------- #
# Subtítulos karaoke: agrupamos palabras en "chunks" de pantalla
# --------------------------------------------------------------------------- #
def build_chunks(timings: list, max_words: int = 3) -> list:
    """Agrupa palabras en bloques de <= max_words; cada bloque con su rango t."""
    chunks = []
    for i in range(0, len(timings), max_words):
        grp = timings[i:i + max_words]
        words = [w for (w, _, _) in grp]
        t0 = grp[0][1]
        t1 = grp[-1][2]
        chunks.append({"words": words, "t0": t0, "t1": t1,
                       "wt": [(w, s, e) for (w, s, e) in grp]})
    return chunks


# --------------------------------------------------------------------------- #
# RENDER DE FOTOGRAMAS
# --------------------------------------------------------------------------- #
def _kenburns(src: Image.Image, box: int, p: float) -> Image.Image:
    """Devuelve un recorte 'box x box' con zoom-in lento + leve paneo (p in 0..1)."""
    canvas = fit_cover(src, int(box * 1.22), int(box * 1.22))
    e = smooth(p)
    win = int(round(box * 1.22 - box * 0.22 * e))     # 1.22*box -> 1.0*box
    max_x = canvas.width - win
    max_y = canvas.height - win
    x0 = int(max_x * (0.5 + 0.15 * e))                # leve paneo horizontal
    y0 = int(max_y * 0.5)
    crop = canvas.crop((x0, y0, x0 + win, y0 + win))
    return crop.resize((box, box), Image.LANCZOS)


def _bottom_scrim(img: Image.Image) -> None:
    """Degradado oscuro inferior para que el texto se lea siempre."""
    grad = Image.new("L", (1, HEIGHT), 0)
    for y in range(HEIGHT):
        a = 0 if y < HEIGHT * 0.55 else int(190 * (y - HEIGHT * 0.55) / (HEIGHT * 0.45))
        grad.putpixel((0, y), min(190, a))
    grad = grad.resize((WIDTH, HEIGHT))
    black = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
    img.paste(black, (0, 0), grad)


def render_product_frame(seg: dict, t: float) -> Image.Image:
    dur = seg["duration"]
    p = t / dur if dur else 0

    # Fondo difuminado (precalculado) + foto con Ken Burns.
    img = seg["bg"].copy()
    box = 880
    photo = _kenburns(seg["photo"], box, p)
    img.paste(photo, ((WIDTH - box) // 2, 300))

    _bottom_scrim(img)
    d = ImageDraw.Draw(img)

    # Badge de precio (sticker arriba-derecha) con 'pop' al entrar.
    pop = back_out(min(1.0, t / 0.45))
    _draw_price_sticker(img, seg["price"], scale=pop)

    # Karaoke: bloque activo de palabras, palabra hablada en amarillo.
    _draw_karaoke(d, seg["chunks"], t)
    return img


def _draw_price_sticker(img: Image.Image, price: float, scale: float):
    pstr = price_str(price)
    fnt = font(96)
    tmp = Image.new("RGBA", (700, 220), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    tw = td.textlength(pstr, font=fnt)
    pad_x, pad_y = 44, 22
    bw, bh = int(tw + 2 * pad_x), int(sum(fnt.getmetrics()) + 2 * pad_y)
    td.rounded_rectangle([0, 0, bw, bh], radius=34, fill=ACCENT)
    td.text((pad_x, pad_y), pstr, font=fnt, fill=WHITE, stroke_width=3,
            stroke_fill=BLACK)
    sticker = tmp.crop((0, 0, bw, bh)).rotate(8, expand=True, resample=Image.BICUBIC)
    if scale <= 0:
        return
    sw, sh = int(sticker.width * scale), int(sticker.height * scale)
    if sw < 1 or sh < 1:
        return
    sticker = sticker.resize((sw, sh), Image.LANCZOS)
    img.paste(sticker, (WIDTH - sw - 60, 250), sticker)


def _draw_karaoke(d, chunks, t):
    active = None
    for c in chunks:
        if c["t0"] <= t <= c["t1"] + 0.25:
            active = c
            break
    if active is None and chunks:
        active = chunks[0] if t < chunks[0]["t0"] else chunks[-1]
    if not active:
        return

    fnt = font(72)
    # 'pop' al cambiar de bloque
    appear = smooth(min(1.0, (t - active["t0"]) / 0.18 + 0.0001))
    size = int(72 * (0.86 + 0.14 * appear))
    fnt = font(size)

    words = [strip_emoji(w) for w in active["words"]]
    gap = d.textlength(" ", font=fnt)
    widths = [d.textlength(w, font=fnt) for w in words]
    total = sum(widths) + gap * (len(words) - 1)
    x = (WIDTH - total) / 2
    y = HEIGHT - 470
    for w, (word, s, e) in zip(words, active["wt"]):
        spoken = t >= s
        fill = YELLOW if (s <= t <= e + 0.12) else (WHITE if spoken else (210, 210, 210))
        d.text((x, y), w, font=fnt, fill=fill, stroke_width=6, stroke_fill=BLACK)
        x += d.textlength(w, font=fnt) + gap


def render_hook_frame(seg: dict, t: float) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(img)
    appear = back_out(min(1.0, t / 0.5))
    base = 104
    size = max(10, int(base * (0.7 + 0.3 * appear)))
    fnt = font(size)
    lines = wrap(d, seg["text"].upper(), fnt, WIDTH - 160)
    lh = sum(fnt.getmetrics()) + 14
    y = (HEIGHT - lh * len(lines)) // 2
    for ln in lines:
        text_centered(d, ln, fnt, y, fill=WHITE, stroke=8)
        y += lh
    text_centered(d, "FindsES", font(52), HEIGHT - 230, fill=ACCENT, stroke=4)
    return img


def render_outro_frame(seg: dict, t: float) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(img)
    y = HEIGHT // 2 - 340
    text_centered(d, strip_emoji(CLAIM_LINE_1), font(58), y, fill=WHITE, stroke=5)
    text_centered(d, strip_emoji(CLAIM_LINE_2), font(58), y + 90, fill=WHITE, stroke=5)
    # CTA con pulso
    pulse = 1 + 0.05 * math.sin(t * 6)
    cta = font(int(92 * pulse))
    text_centered(d, "ÚNETE AL DISCORD", cta, y + 230, fill=ACCENT, stroke=7)
    if seg.get("discord"):
        text_centered(d, seg["discord"].replace("https://", ""),
                      font(46), y + 390, fill=WHITE, stroke=4)
    # flecha
    text_centered(d, "v", font(80), y + 470, fill=WHITE, stroke=5)
    return img


RENDERERS = {
    "hook": render_hook_frame,
    "product": render_product_frame,
    "outro": render_outro_frame,
}


# --------------------------------------------------------------------------- #
# Ensamblado de audio (un .wav del largo total, voz alineada por segmento)
# --------------------------------------------------------------------------- #
def build_audio(segments: list) -> Path:
    parts = []
    for i, seg in enumerate(segments):
        seg_wav = TMP_DIR / f"seg_audio_{i:03d}.wav"
        dur = seg["duration"]
        if seg.get("audio"):
            cmd = [FFMPEG, "-y", "-i", str(seg["audio"]),
                   "-af", "apad", "-t", f"{dur:.3f}",
                   "-ar", "44100", "-ac", "2", str(seg_wav)]
        else:
            cmd = [FFMPEG, "-y", "-f", "lavfi",
                   "-i", "anullsrc=r=44100:cl=stereo",
                   "-t", f"{dur:.3f}", str(seg_wav)]
        subprocess.run(cmd, check=True, capture_output=True)
        parts.append(seg_wav)

    listfile = TMP_DIR / "audio_concat.txt"
    listfile.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in parts))
    full = TMP_DIR / "audio_full.wav"
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0",
                    "-i", str(listfile), "-ar", "44100", "-ac", "2", str(full)],
                   check=True, capture_output=True)
    return full


def render_video(segments: list, out_path: Path, music: Path | None) -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Vídeo mudo: enviamos los fotogramas crudos a ffmpeg por una tubería.
    silent = TMP_DIR / "video_silent.mp4"
    proc = subprocess.Popen([
        FFMPEG, "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
        "-video_size", f"{WIDTH}x{HEIGHT}", "-framerate", str(FPS),
        "-i", "pipe:0", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "veryfast", "-crf", "20", str(silent),
    ], stdin=subprocess.PIPE)

    for seg in segments:
        render = RENDERERS[seg["kind"]]
        nframes = max(1, round(seg["duration"] * FPS))
        for f in range(nframes):
            frame = render(seg, f / FPS).convert("RGB")
            proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falló codificando los fotogramas")

    # 2) Pista de audio del largo total.
    audio = build_audio(segments)

    # 3) Mezcla final (vídeo + voz + música opcional).
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [FFMPEG, "-y", "-i", str(silent), "-i", str(audio)]
    if music and music.exists():
        cmd += ["-stream_loop", "-1", "-i", str(music),
                "-filter_complex",
                "[2:a]volume=0.16[m];[1:a][m]amix=inputs=2:duration=first[a]",
                "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a"]
    cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart", str(out_path)]
    subprocess.run(cmd, check=True, capture_output=True)


# --------------------------------------------------------------------------- #
# Orquestación
# --------------------------------------------------------------------------- #
def pick_products(catalog, category, count):
    prods = catalog["productos"]
    if category:
        cat_l = category.lower()
        prods = [p for p in prods if cat_l in strip_emoji(p["categoria"]).lower()]
    return [p for p in prods if p["fotos"]][:count]


def narration_for(p) -> str:
    return f"{strip_emoji(p['producto'])}. Por solo {price_str(p['precio_eur'])}, con QC real."


def make_bg(photo: Image.Image) -> Image.Image:
    bg = fit_cover(photo, WIDTH, HEIGHT).filter(ImageFilter.GaussianBlur(45))
    return Image.blend(bg, Image.new("RGB", (WIDTH, HEIGHT), BLACK), 0.5)


def run(args) -> int:
    load_env()
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    discord = (catalog["meta"].get("discord") or "").replace("https://", "")
    products = pick_products(catalog, args.category, args.count)
    if not products:
        print("No hay productos para ese filtro.", file=sys.stderr)
        return 1

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    cat_label = strip_emoji(products[0]["categoria"]).upper()

    segments = [{
        "kind": "hook",
        "text": args.hook or f"{len(products)} FINDS DE {cat_label}",
        "duration": HOOK_SECONDS,
        "audio": None,
    }]

    print(f"Generando {len(products)} productos"
          f"{' (DEMO)' if args.demo else ''}...")
    for i, p in enumerate(products):
        photo = (placeholder_photo(p["producto"], i) if args.demo
                 else _safe_photo(p, i))
        narration = narration_for(p)
        audio, timings, dur = get_voice(narration, i, args.demo)
        segments.append({
            "kind": "product",
            "photo": photo,
            "bg": make_bg(photo),
            "price": p["precio_eur"],
            "chunks": build_chunks(timings),
            "duration": dur,
            "audio": audio,
        })
        print(f"  [{i+1}/{len(products)}] {strip_emoji(p['producto'])} "
              f"— {price_str(p['precio_eur'])} ({dur:.1f}s)")

    segments.append({
        "kind": "outro", "discord": discord,
        "duration": OUTRO_SECONDS, "audio": None,
    })

    out = OUT_DIR / args.output
    print("Renderizando (fotograma a fotograma)...")
    render_video(segments, out, Path(args.music) if args.music else None)

    total = sum(s["duration"] for s in segments)
    print(f"\n[OK] Vídeo: {out}")
    print(f"     ~{total:.1f}s · {WIDTH}x{HEIGHT} · "
          f"{out.stat().st_size/1_000_000:.1f} MB")
    return 0


def _safe_photo(p, i):
    try:
        return download_photo(p["fotos"][0])
    except Exception as e:
        print(f"  Foto falló ({e}); placeholder.", file=sys.stderr)
        return placeholder_photo(p["producto"], i)


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera un short pro de FindsES.")
    ap.add_argument("--catalog", default="catalog.json")
    ap.add_argument("--category")
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--hook")
    ap.add_argument("--music")
    ap.add_argument("--output", default="short.mp4")
    ap.add_argument("--demo", action="store_true")
    return run(ap.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
