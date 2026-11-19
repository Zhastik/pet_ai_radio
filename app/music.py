import io
import random
import wave
from enum import Enum


class Genre(str, Enum):
    LOFI = "lofi"
    JAZZ = "jazz"
    AMBIENT = "ambient"
    HOUSE = "house"
    ROCK = "rock"


STATIONS = {
    Genre.LOFI: ("Lo-fi", "lo-fi hip-hop, dusty drums, mellow Rhodes piano"),
    Genre.JAZZ: ("Джаз", "small jazz trio, brushed drums, upright bass and piano"),
    Genre.AMBIENT: ("Эмбиент", "ambient soundscape, evolving pads and soft textures"),
    Genre.HOUSE: ("Хаус", "deep house, steady four-on-the-floor beat and warm bass"),
    Genre.ROCK: ("Рок", "instrumental indie rock, layered electric guitars and live drums"),
}


class MusicGenerator:
    def __init__(self):
        self._backend = None

    def generate(self, genre: Genre) -> bytes:
        import numpy as np
        import torch
        from transformers import AutoProcessor, MusicgenForConditionalGeneration

        if self._backend is None:
            model_id = "facebook/musicgen-small"
            device = "cuda" if torch.cuda.is_available() else "cpu"
            processor = AutoProcessor.from_pretrained(model_id)
            model = MusicgenForConditionalGeneration.from_pretrained(
                model_id, use_safetensors=True
            )
            model.to(device).eval()
            self._backend = processor, model, device

        processor, model, device = self._backend
        mood = random.choice(("dreamy", "warm", "melancholic", "uplifting"))
        prompt = f"{STATIONS[genre][1]}, {mood}, instrumental, no vocals"
        inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(device)
        with torch.inference_mode():
            audio = model.generate(**inputs, do_sample=True, max_new_tokens=1000)

        samples = audio[0, 0].float().cpu().numpy()
        pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2")
        output = io.BytesIO()
        with wave.open(output, "wb") as wav:
            wav.setparams((1, 2, model.config.audio_encoder.sampling_rate, 0, "NONE", ""))
            wav.writeframes(pcm.tobytes())
        return output.getvalue()
