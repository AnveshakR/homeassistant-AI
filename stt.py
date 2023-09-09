from transformers import WhisperProcessor, WhisperForConditionalGeneration
from pydub import AudioSegment
import numpy as np
import io

processor = WhisperProcessor.from_pretrained("openai/whisper-tiny.en")

model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny.en")

model.config.forced_decoder_ids = None

def process_from_audio_data(audio_file, file_type):
    if file_type == 'saved':
        audio = AudioSegment.from_mp3(audio_file)
        print(audio.sample_width, audio.channels, audio)
    elif file_type == 'raw':
        audio = AudioSegment.from_file_using_temporary_files(io.BytesIO(audio_file), format="mp3")

    sample_rate = 16000

    audio = audio.set_frame_rate(sample_rate)
    
    audio = audio.set_channels(1) # Convert to mono
    
    # Convert audio to NumPy array and normalize
    audio_array = np.array(audio.get_array_of_samples())
    audio_array = audio_array / 32768.0 
    input_features = processor(audio_array, sampling_rate=sample_rate, return_tensors='pt').input_features
    predicted_ids = model.generate(input_features)

    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    return transcription[0]

if __name__ == "__main__":
    print(process_from_audio_data('394822261108113409.mp3', 'saved'))