import asyncio, edge_tts

async def main():
    voices = await edge_tts.list_voices()
    es_female = [v for v in voices if v['Locale'].startswith('es') and v['Gender'] == 'Female']
    for v in es_female:
        print(f"{v['ShortName']} - {v['Locale']}")
    print("---")
    mx_female = [v for v in voices if v['Locale'].startswith('es-MX') and v['Gender'] == 'Female']
    for v in mx_female:
        print(f"{v['ShortName']} - {v['Locale']}")

asyncio.run(main())
