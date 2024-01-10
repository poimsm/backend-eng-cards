import os
import uuid
import ffmpeg

def audio_converter(audio_file):
    unique_id = uuid.uuid4()
    input_filename = f'{unique_id}.aac'
    output_filename = f'{unique_id}.webm'

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    audios_dir = os.path.join(base_dir, 'audios')

    if not os.path.exists(audios_dir):
        os.makedirs(audios_dir)

    path_input = os.path.join(audios_dir, input_filename)
    path_output = os.path.join(audios_dir, output_filename)

    with open(path_input, 'wb+') as f:
        for chunk in audio_file.chunks():
            f.write(chunk)

    stream = ffmpeg.input(path_input)
    audio = stream.audio
    stream = ffmpeg.output(audio, path_output, format='webm', acodec='libvorbis')
    ffmpeg.run(stream)

    # Obtener la información del archivo de entrada
    probe = ffmpeg.probe(path_input)
    audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    duration_seconds = float(audio_info['duration'])

    # Opcional: Eliminar el archivo de entrada después de la conversión
    # os.remove(path_input)

    return path_output, duration_seconds
