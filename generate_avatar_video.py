"""
VideoAgent AI - Generador OPTIMIZADO con Avatar Femenino
  - Voz femenina natural (edge-tts Elvira)
  - Avatar con lip-sync pre-renderizado
  - Backgrounds animados
  - Renderizado eficiente
"""

import asyncio, os, random, struct
from pathlib import Path
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = BASE_DIR / "storage" / "temp"
OUTPUT_DIR = BASE_DIR / "storage" / "exports"
TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1080, 1920
FPS = 24
AVATAR_W, AVATAR_H = 500, 700

# ============================================================
# SCRIPT COMPACTO (~11 min objetivo)
# ============================================================
SCRIPT_SECTIONS = [
    {"title": "Introduccion a USFans",
     "narration": "Bienvenidos a este video completo sobre USFans, el agente de compras chino que esta revolucionando la forma en que compramos desde China. Si alguna vez has querido comprar ropa de marca, accesorios o electronicos directamente de Taobao, Weidian o 1688 pero no sabes como, este video es para ti. Hoy te explicare paso a paso que es USFans, como funciona, cuanto cuesta, que productos puedes comprar y si realmente vale la pena. Al final tendras toda la informacion para hacer tu primer pedido con confianza."},
    {"title": "Que es un Agente de Compras",
     "narration": "Antes de entrar en USFans, entendamos que es un agente de compras. China tiene plataformas masivas como Taobao, 1688 y Weidian, pero estan en chino y no aceptan pagos internacionales ni envian al extranjero. Un agente es un intermediario que compra por ti, almacena los productos, toma fotos de control de calidad y te los envia a tu pais. Hacen todo el trabajo pesado para que comprar desde China sea tan facil como comprar en Amazon."},
    {"title": "Historia de USFans",
     "narration": "USFans nacio como solucion para la comunidad internacional que queria acceder a productos chinos de alta calidad a precios de fabrica. Crecio rapidamente gracias a su enfoque en transparencia y servicio al cliente. Hoy tiene cientos de miles de usuarios en Estados Unidos, Europa y Latinoamerica. El nombre combina US, que significa Estados Unidos o nosotros, y Fans, los seguidores. Ofrece almacenamiento, control de calidad y envios a mas de 200 paises."},
    {"title": "Como Funciona Paso a Paso",
     "narration": "Te explico paso a paso como usar USFans. Primero, encuentras un producto en Taobao, 1688 o Weidian. Copias el enlace y lo pegas en USFans. La plataforma te muestra el precio en tu moneda. Anyades al carrito y pagas con PayPal o tarjeta. USFans compra al vendedor chino, el producto llega a su almacen, solicitas fotos QC gratuitas, verificas la calidad, confirmas el envio internacional, eliges metodo de logistica y recibes tu producto en casa. Todo desde el panel de control."},
    {"title": "Precios y Tarifas",
     "narration": "USFans cobra comision del 5 al 10 por ciento sobre el precio del producto. No inflan los precios, a diferencia de otros agentes que marcan hasta un 30 por ciento sin que te enteres. Los envios varian segun peso y destino. La opcion economica tarda 20-30 dias, la expresa 5-7 dias. Ofrecen almacenamiento gratuito 90 dias para consolidar compras y ahorrar en envio. Los costos son transparentes desde el principio."},
    {"title": "Control de Calidad QC",
     "narration": "Cuando tu producto llega al almacen, puedes solicitar fotos gratuitas de alta resolucion. Verificas talla, color, defectos, costuras. Si algo no te gusta, USFans gestiona la devolucion con el vendedor sin que hables chino. El QC es fundamental especialmente para ropa, porque las tallas chinas son diferentes a las occidentales. Es un servicio que da tranquilidad y seguridad en cada compra."},
    {"title": "Comparativa con Otros Agentes",
     "narration": "Hay competidores como Cnfans, HipoBuy, LitBuy, MuleBuy y el desaparecido PandaBuy. USFans destaca por su interfaz limpia, tarifas transparentes, procesamiento en 1-3 dias y servicio al cliente en menos de 24 horas. Cnfans es mas barato en algunos productos pero menos intuitivo. HipoBuy tiene buenas tarifas de envio pero fotos QC menos detalladas. USFans logra el mejor equilibrio entre precio, facilidad y calidad."},
    {"title": "Que Productos Comprar",
     "narration": "La variedad es impresionante. Ropa de marcas como Nike, Adidas, Gucci, Balenciaga, Essentials, Fear of God. Accesorios: bolsos, cinturones, relojes, joyeria, gafas. Electronicos: auriculares, altavoces, cargadores. Hogar: decoracion, muebles, iluminacion. Juguetes y coleccionables. Si puedes imaginarlo, probablemente lo encuentres en las plataformas chinas a mucho menor precio. La calidad varia, por eso es importante el QC."},
    {"title": "Experiencia de Usuario",
     "narration": "USFans tiene app para iPhone con calificacion de 3.9 estrellas. Desde ahi buscas productos, haces pedidos, ves fotos QC, seleccionas envio y rastreas paquetes en tiempo real. La interfaz esta en ingles y chino, los precios en dolares. Las notificaciones te alertan cuando el producto llega al almacen, cuando las fotos QC estan listas y cuando el paquete sale de China. Es rapida, estable y facil de usar."},
    {"title": "Pros y Contras",
     "narration": "Pros: precios transparentes sin markup, fotos QC gratuitas, almacenamiento 90 dias gratis, interfaz limpia, servicio al cliente 24h, PayPal, envio a 200 paises. Contras: envio economico lento 20-30 dias, tarifas mas altas en productos baratos, retrasos en temporada alta, app solo iPhone. En general, la mayoria de usuarios quedan satisfechos y lo recomiendan como una de las mejores opciones actuales."},
    {"title": "Consejos para tu Primera Compra",
     "narration": "Primero, investiga el vendedor y revisa calificaciones. Segundo, siempre pide fotos QC, especialmente para ropa por las tallas. Tercero, no envies un solo producto, espera a tener varios para consolidar. Cuarto, verifica politicas de aduana de tu pais. Quinto, unite a comunidades en Discord o Telegram para aprender de otros. Sexto, empieza con productos pequenos y baratos para probar."},
    {"title": "La Comunidad USFans",
     "narration": "La comunidad es uno de los mayores valores de USFans. En Telegram hay un grupo con mas de 190 mil miembros compartiendo hallazgos y ofertas. En Discord hay canales dedicados con secciones de ayuda. En TikTok e Instagram hay creadores mostrando sus compras y haciendo reviews. Los compradores experimentados ayudan a los nuevos, comparten enlaces verificados y advierten sobre vendedores problematicos."},
    {"title": "El Futuro",
     "narration": "Alibaba integro su IA Qwen en Taobao para busquedas con lenguaje natural. USFans esta bien posicionado con infraestructura solida y usuarios leales. Pronto veremos envios mas rapidos, mejor seguimiento y mas servicios de valor anyadido como personalizacion de productos. El comercio internacional seguira creciendo y los agentes seran clave para acceder a productos chinos."},
    {"title": "Preguntas Frecuentes",
     "narration": "Es seguro? Si, usan PayPal con proteccion al comprador. Cuanto tarda? Economico 20-30 dias, estandar 10-15, expreso 5-7. Puedo devolver? Si, si el QC muestra problemas. Limite de peso? No estricto, pero mas de 10kg puede tener restricciones. Seguro? Si, la mayoria de envios tienen seguro. Necesito chino? No, para eso esta USFans. Replicas? Tienen politicas contra productos ilegales."},
    {"title": "Conclusion",
     "narration": "Hemos visto que es USFans, como funciona, sus costos, productos, ventajas y desventajas. Es una excelente opcion para comprar desde China de manera segura y transparente. Si te fue util, dale like y suscribete para mas contenido sobre compras internacionales. Deja tus preguntas en comentarios. Muchas gracias y nos vemos en el proximo video."},
]

TOTAL_SEC = len(SCRIPT_SECTIONS)

# ============================================================
# AVATAR FEMENINO - PRERENDERIZADO DE ESTADOS
# ============================================================
def _create_avatar(mouth_openness, blink):
    """Crea frame de avatar. Retorna numpy array RGBA."""
    img = Image.new("RGBA", (AVATAR_W, AVATAR_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    skin = (235, 195, 160, 255)
    cx, cy = AVATAR_W//2, 250
    hr = 130

    # Cabeza
    draw.ellipse([cx-hr, cy-hr, cx+hr, cy+hr], fill=skin)
    # Cabello
    draw.ellipse([cx-140, cy-140, cx+140, cy+80], fill=(60, 30, 20, 255))
    # Ojos
    eye_y, eye_sp = cy-20, 50
    if blink:
        for ex in [cx-eye_sp, cx+eye_sp]:
            draw.rectangle([ex-18, eye_y-2, ex+18, eye_y+2], fill=(80,60,40,255))
    else:
        for ex in [cx-eye_sp, cx+eye_sp]:
            draw.ellipse([ex-20, eye_y-12, ex+20, eye_y+12], fill=(255,255,255,255))
            draw.ellipse([ex-8, eye_y-10, ex+8, eye_y+10], fill=(80,60,40,255))
            draw.ellipse([ex-4, eye_y-6, ex+4, eye_y+6], fill=(20,15,10,255))
            draw.ellipse([ex+2, eye_y-8, ex+6, eye_y-4], fill=(255,255,255,180))
    # Cejas
    for bx in [cx-eye_sp, cx+eye_sp]:
        draw.arc([bx-22, eye_y-32, bx+22, eye_y-18], 0, 180, fill=(50,25,15,255), width=4)
    # Nariz
    draw.ellipse([cx-5, cy+8, cx+5, cy+22], fill=(210,175,145,255))
    draw.line([cx, cy+5, cx-3, cy+15], fill=(200,165,135,180), width=2)

    # Boca lip-sync
    mx, my = cx, cy+50
    mw = 45
    if mouth_openness < 0.1:
        draw.arc([mx-mw, my-3, mx+mw, my+3], 0, 180, fill=(160,80,80,255), width=4)
    elif mouth_openness < 0.35:
        draw.ellipse([mx-mw, my-8, mx+mw, my+8], fill=(180,90,90,255))
        draw.ellipse([mx-mw+4, my-4, mx+mw-4, my+4], fill=(220,120,120,255))
    elif mouth_openness < 0.65:
        draw.ellipse([mx-mw, my-14, mx+mw, my+14], fill=(180,90,90,255))
        draw.ellipse([mx-mw+4, my-8, mx+mw-4, my+8], fill=(220,120,120,255))
    else:
        draw.ellipse([mx-mw-5, my-18, mx+mw+5, my+18], fill=(160,80,80,255))
        draw.ellipse([mx-mw, my-10, mx+mw, my+10], fill=(220,120,120,255))

    # Colorete
    for bx in [cx-85, cx+85]:
        draw.ellipse([bx-20, cy+20, bx+20, cy+50], fill=(240,170,160,80))
    # Cuello
    draw.rectangle([cx-30, cy+hr-20, cx+30, cy+hr+50], fill=skin)
    # Cuerpo
    draw.polygon([(cx-180, cy+hr+50), (cx-80, cy+hr+10), (cx+80, cy+hr+10),
                   (cx+180, cy+hr+50), (cx+200, cy+hr+110), (cx-200, cy+hr+110)],
                  fill=(220, 100, 140, 255))
    # Suavizado y redimension
    img = img.filter(ImageFilter.SMOOTH).resize((int(AVATAR_W*0.75), int(AVATAR_H*0.75)), Image.LANCZOS)
    return np.array(img)


# Pre-renderizar los 10 estados del avatar (5 bocas x 2 parpadeo)
print("Pre-renderizando estados del avatar...")
AVATAR_STATES = {}
for mob in [0.0, 0.25, 0.5, 0.75, 1.0]:
    for blk in [False, True]:
        key = (mob, blk)
        AVATAR_STATES[key] = _create_avatar(mob, blk)
print(f"  {len(AVATAR_STATES)} estados renderizados")


# ============================================================
# BACKGROUNDS
# ============================================================
def _create_bg(title, idx):
    colors = [(25,20,45),(45,20,35),(20,40,40),(35,25,50),(50,25,25),
              (25,35,50),(40,20,45),(20,45,35),(50,30,20),(30,40,25),
              (45,25,35),(20,50,40),(55,20,30),(25,45,30),(40,35,20)]
    bg_c = colors[idx % len(colors)]
    img = Image.new("RGB", (WIDTH, HEIGHT), bg_c)
    draw = ImageDraw.Draw(img)
    try:
        ft = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 60)
        fs = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 32)
        fn = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 100)
    except:
        ft = fs = fn = ImageFont.load_default()
    # Decoracion
    for _ in range(5):
        x, y = random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)
        r = random.randint(40, 120)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(*[min(255,c+25) for c in bg_c], 25))
    # Linea
    draw.rectangle([100, HEIGHT//2-60, WIDTH-100, HEIGHT//2-56], fill=(255,255,255,50))
    # Numero
    nt = f"{idx+1:02d}"
    bb = draw.textbbox((0,0), nt, font=fn)
    draw.text(((WIDTH-(bb[2]-bb[0]))//2, HEIGHT//2-180), nt, fill=(255,255,255,30), font=fn)
    # Titulo
    bb = draw.textbbox((0,0), title.upper(), font=ft)
    tw = bb[2]-bb[0]
    draw.text(((WIDTH-tw)//2, HEIGHT//2-20), title.upper(), fill="white", font=ft)
    # Progreso
    st = f"Seccion {idx+1} de {len(SCRIPT_SECTIONS)}"
    bb = draw.textbbox((0,0), st, font=fs)
    tw = bb[2]-bb[0]
    draw.text(((WIDTH-tw)//2, HEIGHT//2+40), st, fill=(200,200,255,150), font=fs)
    # Barra
    bw = int(WIDTH*0.5)
    bx = (WIDTH-bw)//2
    draw.rectangle([bx, HEIGHT-60, bx+bw, HEIGHT-56], fill=(255,255,255,25))
    pw = int(bw*(idx+1)/len(SCRIPT_SECTIONS))
    draw.rectangle([bx, HEIGHT-60, bx+pw, HEIGHT-56], fill=(150,120,255,130))
    return np.array(img)


# ============================================================
# VOZ FEMENINA
# ============================================================
async def _gen_voice(text, idx):
    ap = TEMP_DIR / f"audio_f_{idx:03d}.mp3"
    if not ap.exists():
        import edge_tts
        await edge_tts.Communicate(text, "es-ES-ElviraNeural").save(str(ap))
    return ap

def _analyze_audio(audio_path, fps=FPS):
    """Analiza amplitud para lip-sync. Retorna lista de valores 0-1 por frame."""
    try:
        from moviepy import AudioFileClip
        clip = AudioFileClip(str(audio_path))
        s = clip.to_soundarray(fps=fps, nbytes=2)
        mono = s.mean(axis=1) if s.ndim > 1 else s
        amps = np.abs(mono)
        ma = amps.max()
        if ma > 0: amps = amps / ma
        # Suavizar
        w = max(1, fps//8)
        k = np.ones(w)/w
        sm = np.convolve(amps, k, mode='same')
        op = 1.0/(1.0+np.exp(-8*(sm-0.18)))
        clip.close()
        return np.clip(op, 0, 1).tolist()
    except Exception as e:
        print(f"  Lip-sync fallback: {e}")
        return [0.3]*100


# ============================================================
# COMPOSICION PRINCIPAL
# ============================================================
async def main():
    print("\n=== VIDEO USFANS CON AVATAR FEMENINO ===\n")

    # 1. Voces
    print("[1/4] Generando voz femenina (es-ES-ElviraNeural)...")
    audios, durations = [], []
    for i, sec in enumerate(SCRIPT_SECTIONS):
        ap = await _gen_voice(sec["narration"], i)
        from moviepy import AudioFileClip
        with AudioFileClip(str(ap)) as c:
            d = c.duration
        audios.append(ap)
        durations.append(d)
        print(f"  [{i+1}/{len(SCRIPT_SECTIONS)}] {d:.1f}s")

    total_secs = sum(durations)
    print(f"\n  Duracion total: {total_secs:.1f}s ({total_secs/60:.1f} min)\n")

    # 2. Backgrounds
    print("[2/4] Generando backgrounds...")
    bgs = [_create_bg(sec["title"], i) for i, sec in enumerate(SCRIPT_SECTIONS)]

    # 3. Lip-sync
    print("[3/4] Analizando audio para lip-sync...")
    lips = [_analyze_audio(str(ap)) for ap in audios]
    print(f"  Frames totales: {sum(len(l) for l in lips)}")

    # 4. Componer video
    print("[4/4] Componiendo video con avatar...")
    from moviepy import (
        ImageClip, AudioFileClip, CompositeVideoClip,
        concatenate_videoclips, VideoClip
    )

    segments = []
    for i in range(len(SCRIPT_SECTIONS)):
        dur = durations[i]
        amps = lips[i]
        nf = max(1, int(dur * FPS))

        # Background clip
        bg_clip = ImageClip(bgs[i], duration=dur)
        bg_clip = bg_clip.resized((WIDTH, HEIGHT))

        # Avatar animado frame a frame
        def make_af(t, amps=amps, dur=dur):
            idx = min(int(t/dur*len(amps)), len(amps)-1)
            opn = amps[idx] if idx < len(amps) else 0.3
            mob = round(opn*4)/4
            blk = (int(t*FPS) % 120) > 115
            return AVATAR_STATES[(mob, blk)]

        avatar_clip = VideoClip(make_af, duration=dur)
        avatar_clip = avatar_clip.with_position((WIDTH//2 - AVATAR_W*0.75//2, HEIGHT-520))

        # Composicion
        comp = CompositeVideoClip([bg_clip, avatar_clip], size=(WIDTH, HEIGHT))
        comp = comp.with_audio(AudioFileClip(str(audios[i])))
        segments.append(comp)

        if (i+1) % 5 == 0:
            print(f"  Procesados {i+1}/{len(SCRIPT_SECTIONS)} segmentos")

    print(f"  Uniendo {len(segments)} segmentos...")
    final = concatenate_videoclips(segments, method="compose")

    output = OUTPUT_DIR / "USFans_Avatar_Femenino_Completo.mp4"
    print(f"\n  Renderizando: {output}")
    print(f"  Duracion: {final.duration:.1f}s ({final.duration/60:.1f} min)")
    print(f"  Resolucion: {WIDTH}x{HEIGHT} @ {FPS}fps")
    print(f"  Esto puede tomar varios minutos...\n")

    final.write_videofile(
        str(output), codec="libx264", audio_codec="aac",
        fps=FPS, preset="medium", bitrate="4000k",
        threads=4, logger=None,
    )

    final.close()
    for c in segments:
        try: c.close()
        except: pass

    mb = output.stat().st_size / 1_000_000
    print(f"\n{'='*60}")
    print(f"[OK] VIDEO CON AVATAR GENERADO")
    print(f"[RUTA] {output}")
    print(f"[DURACION] {final.duration:.1f}s ({final.duration/60:.1f} min)")
    print(f"[TAMANO] {mb:.1f} MB")
    print(f"{'='*60}")


if __name__ == "__main__":
    t0 = datetime.now()
    asyncio.run(main())
    t = (datetime.now()-t0).total_seconds()
    print(f"Tiempo total: {t:.1f}s ({t/60:.1f} min)")
