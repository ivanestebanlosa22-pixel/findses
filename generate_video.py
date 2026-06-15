"""
VideoAgent AI - Generador directo de video sobre USFans
Genera un video de 11 minutos sobre USFans (agente de compras chino)
Sin necesidad de API keys externas
"""

import asyncio
import os
import json
import math
from pathlib import Path
from datetime import datetime

# Configuración
OUTPUT_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "storage" / "exports"
TEMP_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "storage" / "temp"
PROJECT_NAME = "usfans_video"
TARGET_DURATION = 660  # 11 minutos en segundos

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# SCRIPT DEL VIDEO - USFans: El Agente de Compras Chino
# ============================================================

# Cada sección tiene bastante texto para alcanzar ~11 minutos de habla.
# Aprox 18-20 caracteres por segundo en español.
# 660s * 18 = 11,880 caracteres necesarios. Este script tiene ~13,000.
SCRIPT_SECTIONS = [
    {
        "title": "Introduccion a USFans",
        "duration": 45,
        "narration": (
            "Bienvenidos a este video completo sobre USFans, el agente de compras chino "
            "que esta revolucionando la forma en que compramos productos desde China. "
            "Si alguna vez has querido comprar ropa de marca, accesorios, electronicos o cualquier "
            "producto directamente de Taobao, Weidian o 1688 pero no sabes como hacerlo, "
            "este video es para ti. Hoy te voy a explicar paso a paso que es USFans, "
            "como funciona, cuanto cuesta, que productos puedes comprar y si realmente vale la pena. "
            "Al final de este video vas a tener toda la informacion necesaria para hacer tu primer pedido "
            "con confianza y sin miedo a ser estafado. Asi que ponte comodo, "
            "que esto se va a poner interesante."
        ),
        "visual": "presentacion_usfans",
    },
    {
        "title": "Que es un Agente de Compras",
        "duration": 55,
        "narration": (
            "Antes de meternos de lleno en USFans, es importante entender que es un agente de compras. "
            "China tiene las plataformas de e-commerce mas grandes del mundo. Hablamos de Taobao, "
            "que es como el eBay chino pero mucho mas grande, con millones de vendedores y productos. "
            "Luego esta 1688, que es el mercado mayorista donde los precios son incluso mas bajos. "
            "Y Weidian, otra plataforma muy popular para ropa y accesorios. "
            "El problema es que estas plataformas estan completamente en chino, no aceptan tarjetas "
            "internacionales, y la mayoria de vendedores no envian al extranjero. "
            "Aqui es donde entran los agentes de compras. Un agente es basicamente un intermediario "
            "que vive en China y puede comprar los productos por ti. "
            "Tu le dices que producto quieres, ellos lo compran, lo reciben en su almacen, "
            "te toman fotos para que verifiques la calidad, y luego te lo envian a tu pais. "
            "Es un servicio integral que hace que comprar desde China sea tan facil como comprar en Amazon."
        ),
        "visual": "agente_compras",
    },
    {
        "title": "Historia y Origen de USFans",
        "duration": 65,
        "narration": (
            "USFans nacio hace algunos anos como una solucion para la comunidad internacional "
            "que queria acceder a los productos chinos sin tener que lidiar con las barreras idiomaticas "
            "y logisticas. La plataforma fue creada por un equipo con experiencia en comercio internacional "
            "y logistica, que entendia las necesidades de los compradores extranjeros. "
            "A diferencia de otros agentes que empezaron siendo muy pequenos, USFans crecio rapidamente "
            "gracias a su enfoque en la transparencia y la atencion al cliente. "
            "El nombre USFans viene de la combinacion de US, que significa Estados Unidos pero tambien "
            "nosotros en ingles, y Fans, que son los aficionados o seguidores. "
            "La idea era crear una plataforma para los fans de los productos chinos en todo el mundo. "
            "Hoy en dia, USFans tiene cientos de miles de usuarios en Estados Unidos, Europa, "
            "Latinoamerica y otras regiones. La compania ha expandido sus operaciones "
            "y ahora ofrece servicios de almacenamiento, control de calidad, y envios a mas de 200 paises. "
            "Es una historia de exito en el mundo del comercio electronico internacional."
        ),
        "visual": "historia_usfans",
    },
    {
        "title": "Como Funciona USFans Paso a Paso",
        "duration": 80,
        "narration": (
            "Ahora vamos al grano. Te voy a explicar paso a paso como usar USFans para comprar "
            "cualquier producto desde China. El proceso es mucho mas sencillo de lo que imaginas. "
            "Paso uno: encuentras un producto que te guste en Taobao, 1688 o Weidian. "
            "Puedes buscar por categoria, por palabra clave o usando el sistema de busqueda por imagen. "
            "Paso dos: copias el enlace del producto y lo pegas en la barra de busqueda de USFans. "
            "La plataforma automaticamente detecta el producto y te muestra el precio en tu moneda. "
            "Paso tres: anyades el producto a tu carrito y procedes al pago. "
            "USFans acepta PayPal y tarjetas de credito internacionales. "
            "Paso cuatro: una vez que pagas, USFans compra el producto al vendedor chino. "
            "Esto normalmente tarda de 1 a 3 dias habiles. "
            "Paso cinco: el producto llega al almacen de USFans en China. "
            "Aqui es donde puedes solicitar las fotos de control de calidad gratuitas. "
            "Paso seis: revisas las fotos y si todo esta bien, confirmas el envio internacional. "
            "Paso siete: eliges tu metodo de envio y pagas los costos de logistica. "
            "Paso ocho: recibes tu producto en la puerta de tu casa y disfrutas. "
            "Todo el proceso se gestiona desde el panel de control de USFans, "
            "donde puedes ver el estado de tu pedido en tiempo real."
        ),
        "visual": "paso_paso",
    },
    {
        "title": "Precios y Tarifas de USFans",
        "duration": 75,
        "narration": (
            "Hablemos de dinero, que es lo que mas nos interesa a todos. "
            "USFans cobra una comision de servicio que generalmente esta entre el 5 y el 10 por ciento "
            "del precio del producto. Esta comision es bastante estandar en la industria. "
            "Lo bueno es que USFans no infla el precio de los productos. "
            "Muchos otros agentes marcan el precio del producto hacia arriba, a veces hasta un 30 por ciento, "
            "y tu ni te enteras. USFans te muestra el precio real del producto mas su comision, "
            "asi que sabes exactamente cuanto estas pagando. Los costos de envio internacional "
            "varian dependiendo del peso, el tamano del paquete y el destino. "
            "USFans tiene multiples opciones de envio. La mas economica puede tardar entre 20 y 30 dias, "
            "mientras que la opcion expresa puede llegar en 5 a 7 dias. "
            "Los precios de envio son competitivos y se calculan automaticamente cuando seleccionas "
            "los productos que quieres enviar. Ademas, USFans ofrece almacenamiento gratuito "
            "por 90 dias, lo que significa que puedes ir comprando varios productos a lo largo de tres meses "
            "y luego enviarlos todos juntos en un solo paquete, ahorrando mucho en costos de envio."
        ),
        "visual": "precios_tarifas",
    },
    {
        "title": "Control de Calidad QC",
        "duration": 55,
        "narration": (
            "Una de las mejores caracteristicas de USFans es su sistema de control de calidad, "
            "conocido como QC. Cuando tu producto llega al almacen de USFans, tienes la opcion "
            "de solicitar fotos gratuitas de alta resolucion. Esto es increiblemente util porque "
            "puedes ver exactamente lo que vas a recibir antes de pagar el envio internacional. "
            "Puedes verificar que la talla sea la correcta, que el color coincida con las fotos "
            "del anuncio, que no tenga defectos, costuras mal hechas o manchas. "
            "Si algo no te gusta, puedes solicitar una devolucion y USFans se encarga de gestionarla "
            "con el vendedor chino. Esto sin tener que hablar chino ni lidiar con sistemas de devolucion "
            "complicados. El proceso de QC es fundamental cuando compras ropa o calzado, "
            "porque las tallas chinas suelen ser diferentes a las tallas occidentales. "
            "Muchos compradores experimentados recomiendan siempre solicitar las fotos QC "
            "antes de enviar cualquier producto. Es un servicio que te da tranquilidad y seguridad."
        ),
        "visual": "control_calidad",
    },
    {
        "title": "USFans vs Otros Agentes",
        "duration": 85,
        "narration": (
            "Como te imaginaras, USFans no es el unico agente de compras chino en el mercado. "
            "Hay competidores como Cnfans, HipoBuy, LitBuy, MuleBuy, y el ya desaparecido PandaBuy. "
            "Entonces, por que elegir USFans? Vamos a hacer una comparativa detallada. "
            "USFans destaca por su interfaz limpia y profesional. La pagina web y la aplicacion "
            "son faciles de navegar, incluso para alguien que nunca ha usado un agente de compras. "
            "Las tarifas de servicio son transparentes, no hay cargos ocultos. "
            "El tiempo de procesamiento de pedidos es de 1 a 3 dias habiles, que es bastante rapido. "
            "Cnfans, por otro lado, suele tener precios un poco mas bajos en algunos productos, "
            "pero su interfaz es menos intuitiva y el servicio al cliente no es tan rapido. "
            "HipoBuy tiene buenas tarifas de envio, especialmente para paquetes pesados, "
            "pero sus fotos QC no son tan detalladas como las de USFans. "
            "LitBuy es relativamente nuevo y aun esta construyendo su reputacion. "
            "MuleBuy ofrece buenos precios pero tiene menos opciones de personalizacion. "
            "En general, USFans logra un equilibrio excelente entre precio, facilidad de uso, "
            "calidad de servicio y transparencia. Por eso es una de las opciones mas recomendadas "
            "en las comunidades de compradores internacionales."
        ),
        "visual": "comparativa",
    },
    {
        "title": "Tipos de Productos Disponibles",
        "duration": 65,
        "narration": (
            "La variedad de productos que puedes conseguir a traves de USFans es realmente impresionante. "
            "China es el centro de fabricacion del mundo, y a traves de estas plataformas "
            "tienes acceso directo a las fabricas. Encontraras ropa de todos los estilos: "
            "desde marcas de lujo como Gucci, Louis Vuitton o Balenciaga, hasta marcas deportivas "
            "como Nike, Adidas, New Balance, y marcas mas accesibles como Essentials, Fear of God, "
            "Represent, y muchas mas. Tambien hay muchisimos accesorios: bolsos, mochilas, "
            "cinturones, carteras, joyeria, relojes, gafas de sol, gorras. "
            "Electronicos: auriculares, altavoces, cargadores, cables, fundas para telefonos. "
            "Articulos para el hogar: decoracion, muebles, iluminacion, ropa de cama. "
            "Juguetes y coleccionables: figuras de accion, peluches, legos, puzzles. "
            "Incluso cosas mas especificas como material de arte, instrumentos musicales, "
            "o equipo de camping. Si puedes imaginarlo, probablemente puedas comprarlo "
            "en las plataformas chinas a un precio mucho mas bajo que en tu pais. "
            "Eso si, la calidad puede variar mucho, por eso es tan importante el control de calidad."
        ),
        "visual": "productos",
    },
    {
        "title": "Experiencia de Usuario y Aplicacion",
        "duration": 55,
        "narration": (
            "USFans tiene una aplicacion movil disponible para iPhone que puedes descargar "
            "gratis desde la App Store. La aplicacion tiene una calificacion de 3.9 estrellas "
            "y los usuarios destacan su facilidad de uso y diseno moderno. "
            "Desde la aplicacion puedes hacer practicamente todo: buscar productos, "
            "copiar enlaces de Taobao, hacer pedidos, ver el estado de tus compras, "
            "solicitar fotos QC, seleccionar opciones de envio, y rastrear tus paquetes "
            "en tiempo real. La interfaz esta disponible en ingles y chino, "
            "y los precios se muestran en dolares americanos u otras monedas. "
            "Una caracteristica muy util es el sistema de notificaciones: "
            "recibes alertas cuando tu producto llega al almacen, cuando las fotos QC estan listas, "
            "y cuando tu paquete sale de China. La aplicacion es rapida y estable, "
            "aunque algunos usuarios han reportado pequenos bugs de vez en cuando. "
            "En general, la experiencia de usuario es muy positiva, especialmente "
            "si la comparamos con otros agentes que tienen interfaces mas anticuadas."
        ),
        "visual": "app_usfans",
    },
    {
        "title": "Ventajas y Desventajas de USFans",
        "duration": 75,
        "narration": (
            "Como todo servicio, USFans tiene sus pros y sus contras. Vamos a analizarlos "
            "para que puedas tomar una decision informada. "
            "Entre las ventajas: los precios son transparentes, no hay markup oculto en los productos. "
            "Las fotos de control de calidad son gratuitas, algo que no todos los agentes ofrecen. "
            "El almacenamiento es gratuito por 90 dias, lo que te da mucho tiempo para consolidar "
            "compras. La interfaz es limpia y facil de usar. El servicio al cliente responde "
            "en menos de 24 horas y hablan ingles. Aceptan PayPal y tarjetas de credito. "
            "Y tienen envio a mas de 200 paises. Por el lado de las desventajas: "
            "los tiempos de envio economico pueden ser largos, entre 20 y 30 dias. "
            "Las tarifas de servicio son un poco mas altas que las de algunos competidores "
            "para productos de menos de 10 dolares. Ocasionalmente hay retrasos en el procesamiento "
            "durante temporadas altas como el Black Friday o antes del Ano Nuevo Chino. "
            "Y la aplicacion solo esta disponible para iPhone, no para Android. "
            "Pero en general, la mayoria de usuarios estan satisfechos con el servicio "
            "y muchos lo consideran la mejor opcion para comprar desde China actualmente."
        ),
        "visual": "pros_contras",
    },
    {
        "title": "Consejos para tu Primera Compra",
        "duration": 75,
        "narration": (
            "Si es tu primera vez usando USFans, aqui tienes una serie de consejos practicos "
            "que te van a ahorrar dolores de cabeza y dinero. "
            "Primer consejo: investiga bien el producto y el vendedor antes de comprar. "
            "Revisa las calificaciones del vendedor, lee los comentarios de otros compradores, "
            "y mira las fotos reales que han subido. Segundo consejo: siempre, siempre "
            "solicita las fotos de control de calidad antes de enviar. Especialmente para ropa, "
            "porque las tallas chinas son mas pequenas que las occidentales. "
            "Tercer consejo: no te apresures a enviar tu primer producto. Espera a tener "
            "varios productos en el almacen y envialos todos juntos. El costo de envio "
            "por articulo se reduce drasticamente cuando consolidas. "
            "Cuarto consejo: verifica las politicas de aduana de tu pais antes de hacer el pedido. "
            "Algunos paises tienen limites de importacion libres de impuestos, y otros cobran "
            "aranceles elevados. Quinto consejo: unite a comunidades de compradores en Discord, "
            "Telegram o Reddit. Hay grupos con miles de miembros que comparten sus experiencias, "
            "recomendaciones de productos, y advierten sobre vendedores problematicos. "
            "Sexto consejo: empieza con productos pequenos y baratos para probar el servicio. "
            "Una vez que te sientas comodo, puedes arriesgarte con compras mas grandes."
        ),
        "visual": "consejos",
    },
    {
        "title": "La Comunidad de USFans",
        "duration": 55,
        "narration": (
            "Una de las cosas mas valiosas de USFans es su comunidad de usuarios. "
            "En Telegram hay un grupo oficial con mas de 190 mil miembros donde los usuarios "
            "comparten sus hallazgos, las mejores ofertas, y sus experiencias de compra. "
            "Tambien hay numerosos canales en Discord dedicados a USFans y otros agentes, "
            "con secciones para compartir productos, hacer preguntas, y resolver dudas. "
            "En TikTok e Instagram hay creadores de contenido que se dedican a mostrar "
            "sus compras a traves de USFans, haciendo unboxings y reviews de productos. "
            "La comunidad es increiblemente util porque los compradores con experiencia "
            "ayudan a los nuevos, comparten enlaces directos a productos verificados, "
            "y advierten sobre vendedores que no son confiables. "
            "Si vas a empezar a usar USFans, te recomiendo que te unas a estas comunidades. "
            "Te van a servir muchisimo para aprender y para descubrir productos que ni sabias que existian. "
            "La cultura del haul, que es como se llama a las compras masivas desde China, "
            "es toda una subcultura con su propio lenguaje y tradiciones."
        ),
        "visual": "comunidad",
    },
    {
        "title": "El Futuro de las Compras desde China",
        "duration": 60,
        "narration": (
            "El mercado de agentes de compras chinos esta evolucionando muy rapidamente. "
            "Alibaba, la empresa duena de Taobao y Tmall, ha integrado su inteligencia artificial Qwen "
            "en la plataforma, permitiendo a los usuarios buscar productos con lenguaje natural "
            "y recibir recomendaciones personalizadas. Esto va a cambiar la forma en que compramos. "
            "USFans esta bien posicionado para adaptarse a estos cambios tecnologicos. "
            "La empresa tiene una infraestructura solida, relaciones con los mejores transportistas, "
            "y una base de usuarios leales. En el futuro cercano, podemos esperar "
            "tiempos de envio mas rapidos, mejores sistemas de seguimiento, "
            "y probablemente integracion directa con las plataformas chinas para hacer el proceso "
            "aun mas automatico. Tambien es probable que veamos mas servicios de valor anyadido, "
            "como personalizacion de productos, diseno propio, o incluso produccion bajo demanda. "
            "El comercio internacional va a seguir creciendo y los agentes de compras "
            "van a jugar un papel cada vez mas importante en facilitar el acceso "
            "a los productos chinos para el resto del mundo."
        ),
        "visual": "futuro",
    },
    {
        "title": "Preguntas Frecuentes FAQ",
        "duration": 65,
        "narration": (
            "Antes de terminar, quiero responder algunas preguntas frecuentes sobre USFans "
            "que seguramente te estaras haciendo. Primera pregunta: es seguro comprar a traves de USFans? "
            "Si, es seguro. USFans tiene anos de experiencia y miles de usuarios satisfechos. "
            "Usan PayPal que te da proteccion al comprador. Segunda pregunta: cuanto tardan los envios? "
            "Depende del metodo que elijas. El economico tarda 20-30 dias, el estandar 10-15, "
            "y el expreso 5-7 dias. Tercera pregunta: puedo devolver un producto? "
            "Si, si las fotos QC muestran que el producto no es lo que pediste, puedes devolverlo. "
            "Cuarta pregunta: hay limites de peso? No hay limites estrictos, pero paquetes "
            "de mas de 10 kilos pueden tener restricciones en algunos paises. "
            "Quinta pregunta: que pasa si mi paquete se pierde? USFans tiene seguro "
            "para la mayoria de sus metodos de envio, asi que estarias cubierto. "
            "Sexta pregunta: necesito saber chino para comprar? No, para eso esta USFans. "
            "Ellos se encargan de toda la comunicacion con los vendedores. "
            "Septima pregunta: puedo comprar productos prohibidos o replicas? "
            "USFans tiene politicas contra productos ilegales. Las replicas de marcas "
            "pueden ser incautadas en aduana, asi que ten cuidado con lo que compras."
        ),
        "visual": "faq",
    },
    {
        "title": "Conclusion y Despedida",
        "duration": 50,
        "narration": (
            "Bueno, hemos llegado al final de este video completo sobre USFans. "
            "Hemos visto que es, como funciona, cuanto cuesta, que productos puedes comprar, "
            "sus ventajas y desventajas, y te he dado consejos practicos para tu primera compra. "
            "USFans es una excelente opcion si quieres acceder al enorme catalogo de productos chinos "
            "de manera segura, transparente y sin complicaciones. "
            "No es perfecto, pero ningun servicio lo es. Lo importante es que es confiable "
            "y que la mayoria de usuarios quedan satisfechos con su experiencia. "
            "Si este video te ha sido util, te agradezco mucho que le des like, "
            "lo compartas con tus amigos que esten interesados en comprar desde China, "
            "y te suscribas al canal para mas contenido sobre compras internacionales, "
            "hacks de ahorro y reviews de productos. Si tienes alguna pregunta, "
            "dejala en los comentarios y con gusto te respondere. "
            "Muchas gracias por verme y nos vemos en el proximo video. Hasta luego."
        ),
        "visual": "conclusion",
    },
]

# Ajustar duraciones para que sumen exactamente 660 segundos (11 min)
total_planned = sum(s["duration"] for s in SCRIPT_SECTIONS)
scale = TARGET_DURATION / total_planned
for s in SCRIPT_SECTIONS:
    s["duration"] = round(s["duration"] * scale)
# Ajustar el último para que sume exactamente
diff = TARGET_DURATION - sum(s["duration"] for s in SCRIPT_SECTIONS)
SCRIPT_SECTIONS[-1]["duration"] += diff


# ============================================================
# GENERACIÓN DE VOZ CON EDGE-TTS
# ============================================================

async def generate_voice(section: dict, index: int) -> Path:
    """Genera audio para una sección usando edge-tts."""
    audio_file = TEMP_DIR / f"audio_{index:03d}.mp3"
    if audio_file.exists():
        return audio_file

    import edge_tts

    voice = "es-ES-AlvaroNeural"
    rate = "+0%"  # velocidad normal
    communicate = edge_tts.Communicate(
        section["narration"],
        voice,
        rate=rate,
    )
    await communicate.save(str(audio_file))
    print(f"  Audio generado: {audio_file.name}")
    return audio_file


# ============================================================
# GENERACIÓN DE VISUALES (SLIDES)
# ============================================================

def create_slide(texts: list, bg_color: tuple, output_path: Path, width: int = 1080, height: int = 1920):
    """Crea una imagen de slide con texto."""
    from PIL import Image, ImageDraw, ImageFont
    import os

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Buscar fuente
    font_paths = [
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]
    font_path = None
    for fp in font_paths:
        if os.path.exists(fp):
            font_path = fp
            break

    try:
        title_font = ImageFont.truetype(font_path or "arial.ttf", 72) if font_path else ImageFont.load_default()
        subtitle_font = ImageFont.truetype(font_path or "arial.ttf", 48) if font_path else ImageFont.load_default()
    except Exception:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Título principal
    if texts:
        title = texts[0]
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text(((width - tw) // 2, height // 4), title, fill="white", font=title_font)

    # Subtítulos
    y_start = height // 3
    for i, text in enumerate(texts[1:], 1):
        lines = []
        current = ""
        for word in text.split():
            test = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=subtitle_font)
            tw = bbox[2] - bbox[0]
            if tw > width - 100:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)

        for j, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=subtitle_font)
            tw = bbox[2] - bbox[0]
            y_pos = y_start + i * 80 + j * 60
            if y_pos < height - 100:
                draw.text(((width - tw) // 2, y_pos), line, fill="white", font=subtitle_font)

    # Decoración: línea sutil
    draw.rectangle([width//4, height//3 - 30, 3*width//4, height//3 - 25], fill=(100, 100, 255, 200))

    img.save(output_path)
    print(f"  Slide creado: {output_path.name}")


def generate_visuals():
    """Genera todas las imágenes para las secciones."""
    visuals = {}
    color_palette = [
        (20, 22, 40),   # azul oscuro
        (30, 20, 45),   # púrpura
        (20, 40, 35),   # verde oscuro
        (45, 25, 30),   # rojo oscuro
        (25, 35, 50),   # azul medio
        (40, 30, 25),   # naranja oscuro
        (35, 20, 40),   # violeta
        (20, 45, 40),   # teal
        (50, 30, 20),   # marrón
        (30, 30, 50),   # índigo
        (40, 40, 20),   # oliva
        (25, 45, 30),   # verde
        (45, 35, 20),   # cobre
        (35, 45, 25),   # lima oscuro
    ]

    for i, section in enumerate(SCRIPT_SECTIONS):
        bg = color_palette[i % len(color_palette)]
        slide_path = TEMP_DIR / f"slide_{i:03d}.png"
        if not slide_path.exists():
            texts = [
                section["title"],
                "USFans - Agente de Compras Chino",
                f"Sección {i+1} de {len(SCRIPT_SECTIONS)}",
            ]
            visual_key = section["visual"]
            create_slide(texts, bg, slide_path)
        visuals[section["visual"]] = slide_path
        # Also save a mapping by index
        (TEMP_DIR / f"slide_{i:03d}.png").parent.mkdir(parents=True, exist_ok=True)
        if not (TEMP_DIR / f"slide_{i:03d}.png").exists():
            import shutil
            shutil.copy(slide_path, TEMP_DIR / f"slide_{i:03d}.png")

    return visuals


# ============================================================
# GENERACIÓN DE SUBTÍTULOS SRT
# ============================================================

def generate_subtitles(sections: list, audio_durations: list) -> str:
    """Genera archivo SRT con subtítulos."""
    srt_lines = []
    sub_index = 1
    current_time = 0.0

    for i, section in enumerate(sections):
        words = section["narration"].split()
        duration = audio_durations[i] if i < len(audio_durations) else section["duration"]
        words_per_sub = max(1, len(words) // max(1, int(duration / 3)))

        for chunk_start in range(0, len(words), words_per_sub):
            chunk = words[chunk_start:chunk_start + words_per_sub]
            chunk_text = " ".join(chunk)

            seg_duration = (len(chunk) / len(words)) * duration
            start_s = current_time
            end_s = current_time + seg_duration

            def fmt_time(secs):
                h = int(secs // 3600)
                m = int((secs % 3600) // 60)
                s = int(secs % 60)
                ms = int((secs % 1) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

            srt_lines.append(f"{sub_index}")
            srt_lines.append(f"{fmt_time(start_s)} --> {fmt_time(end_s)}")
            srt_lines.append(chunk_text)
            srt_lines.append("")

            sub_index += 1
            current_time = end_s

    return "\n".join(srt_lines)


# ============================================================
# COMPOSICIÓN DEL VIDEO FINAL
# ============================================================

async def compose_video():
    """Compone el video final con todas las secciones."""
    print("\n=== INICIANDO GENERACIÓN DEL VIDEO DE 11 MINUTOS SOBRE USFANS ===\n")

    # Paso 1: Generar audios
    print("Paso 1/4: Generando narración con edge-tts...")
    audio_files = []
    audio_durations = []
    for i, section in enumerate(SCRIPT_SECTIONS):
        print(f"  Generando audio {i+1}/{len(SCRIPT_SECTIONS)}: {section['title']}")
        audio_path = await generate_voice(section, i)

        # Obtener duración real del audio
        try:
            from moviepy import AudioFileClip
            with AudioFileClip(str(audio_path)) as clip:
                real_duration = clip.duration
        except Exception:
            real_duration = section["duration"]

        audio_files.append(audio_path)
        audio_durations.append(real_duration)
        print(f"    Duración: {real_duration:.1f}s (planificado: {section['duration']}s)")

    # Paso 2: Generar slides visuales
    print("\nPaso 2/4: Generando slides visuales...")
    generate_visuals()

    # Paso 3: Generar subtítulos
    print("\nPaso 3/4: Generando subtítulos...")
    srt_content = generate_subtitles(SCRIPT_SECTIONS, audio_durations)
    srt_path = TEMP_DIR / "subtitles.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    # Paso 4: Componer video final
    print("\nPaso 4/4: Componiendo video final (esto puede tomar varios minutos)...")
    from moviepy import (
        ImageClip, AudioFileClip, TextClip, CompositeVideoClip,
        concatenate_videoclips, ColorClip
    )

    WIDTH, HEIGHT = 1080, 1920
    clips = []

    for i, section in enumerate(SCRIPT_SECTIONS):
        slide_path = TEMP_DIR / f"slide_{i:03d}.png"
        audio_path = audio_files[i]
        duration = audio_durations[i]

        if not slide_path.exists():
            slide = ColorClip(color=(20, 22, 40), size=(WIDTH, HEIGHT), duration=duration)
        else:
            slide = ImageClip(str(slide_path), duration=duration)

        if audio_path.exists():
            try:
                audio = AudioFileClip(str(audio_path))
                slide = slide.with_audio(audio)
            except Exception as e:
                print(f"  Error cargando audio {audio_path.name}: {e}")

        clips.append(slide)

    if not clips:
        print("Error: No se pudieron crear clips")
        return

    print(f"  Concatenando {len(clips)} clips...")
    final_video = concatenate_videoclips(clips, method="compose")

    output_path = OUTPUT_DIR / f"USFans_Agente_Compras_Chino_11min.mp4"
    print(f"  Renderizando video a: {output_path}")

    final_video.write_videofile(
        str(output_path),
        codec="libx264",
        audio_codec="aac",
        fps=24,
        preset="medium",
        bitrate="4000k",
        threads=4,
        logger=None,
    )

    final_video.close()
    for clip in clips:
        try:
            clip.close()
        except Exception:
            pass

    # Guardar subtítulos junto al video
    srt_output = output_path.with_suffix(".srt")
    with open(srt_output, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"\n{'='*60}")
    print(f"[OK] VIDEO GENERADO EXITOSAMENTE")
    print(f"[PATH] {output_path}")
    print(f"[DURACION] {sum(audio_durations):.1f} segundos ({sum(audio_durations)/60:.1f} minutos)")
    print(f"[SUBTITULOS] {srt_output}")
    print(f"{'='*60}")

    return output_path


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    start = datetime.now()
    asyncio.run(compose_video())
    elapsed = (datetime.now() - start).total_seconds()
    print(f"\nTiempo total de generación: {elapsed:.1f} segundos ({elapsed/60:.1f} minutos)")
