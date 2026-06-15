"""Script rapido para componer el video final desde los archivos ya generados."""
import sys
from pathlib import Path
from datetime import datetime

TEMP_DIR = Path("C:/Users/ivane/Desktop/video-agent-ai/storage/temp")
OUTPUT_DIR = Path("C:/Users/ivane/Desktop/video-agent-ai/storage/exports")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

WIDTH, HEIGHT = 1080, 1920
NUM_SECTIONS = 15

print("Componiendo video final con 15 secciones...")

clips = []
for i in range(NUM_SECTIONS):
    slide_path = TEMP_DIR / f"slide_{i:03d}.png"
    audio_path = TEMP_DIR / f"audio_{i:03d}.mp3"

    if not audio_path.exists():
        print(f"  Saltando seccion {i}: no hay audio")
        continue

    audio = AudioFileClip(str(audio_path))
    duration = audio.duration

    if slide_path.exists():
        slide = ImageClip(str(slide_path), duration=duration)
    else:
        from moviepy import ColorClip
        slide = ColorClip(color=(20, 22, 40), size=(WIDTH, HEIGHT), duration=duration)

    slide = slide.with_audio(audio)
    clips.append(slide)
    print(f"  Seccion {i+1}/{NUM_SECTIONS}: {duration:.1f}s")

print(f"\nConcatenando {len(clips)} clips...")
final = concatenate_videoclips(clips, method="compose")

output = OUTPUT_DIR / "USFans_Video_Completo_17min.mp4"
print(f"Renderizando video a {output}...")
print(f"Duracion total: {final.duration:.1f}s = {final.duration/60:.1f} min")

final.write_videofile(
    str(output),
    codec="libx264",
    audio_codec="aac",
    fps=24,
    preset="medium",
    bitrate="4000k",
    threads=4,
    logger=None,
)

final.close()
for c in clips:
    try: c.close()
    except: pass

print(f"\n[OK] Video generado: {output}")
print(f"[TAMANO] {output.stat().st_size / 1_000_000:.1f} MB")
print(f"[DURACION] {final.duration:.1f}s")
