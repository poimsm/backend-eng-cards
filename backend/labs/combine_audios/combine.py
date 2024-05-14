from pydub import AudioSegment

def combine_mp3(files):
    # Crea un segmento de audio vacio
    combined = AudioSegment.empty()
    
    # Itera sobre la lista de archivos MP3
    for file in files:
        # Carga el archivo MP3
        audio = AudioSegment.from_mp3(file)
        # Combina el audio actual con el acumulado
        combined += audio
    
    # Exporta el resultado combinado a un nuevo archivo MP3
    combined.export("combined_output.mp3", format="mp3")

# Lista de archivos MP3 a combinar
files = [
    'a01.mp3',
    'a02.mp3',
    'a03.mp3',
    'a04.mp3',
    'a05.mp3',
]

# Llama a la función con la lista de archivos
combine_mp3(files)
