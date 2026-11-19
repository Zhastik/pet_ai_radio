import io
import threading
import unittest
import wave
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.music import Genre


def sample_wav():
    output = io.BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setparams((1, 2, 32000, 0, "NONE", ""))
        wav.writeframes(bytes(64))
    return output.getvalue()


class RadioTests(unittest.TestCase):
    def test_player_lists_available_genres(self):
        with TestClient(app) as client:
            self.assertIn('id="genre"', client.get("/").text)
            self.assertIn({"id": "jazz", "name": "Джаз"}, client.get("/api/genres").json())

    def test_each_track_request_passes_selected_genre_to_generator(self):
        with TestClient(app) as client, patch(
            "app.main.generator.generate", return_value=sample_wav()
        ) as generate:
            for _ in range(2):
                response = client.post("/api/genres/jazz/tracks")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers["content-type"], "audio/wav")
                self.assertEqual(response.headers["cache-control"], "no-store")
                with wave.open(io.BytesIO(response.content), "rb") as wav:
                    self.assertEqual(wav.getframerate(), 32000)
            self.assertEqual(generate.call_count, 2)
            generate.assert_called_with(Genre.JAZZ)
            self.assertEqual(client.post("/api/genres/unknown/tracks").status_code, 422)
            self.assertEqual(generate.call_count, 2)

    def test_busy_generator_returns_retry_delay_and_recovers(self):
        started = threading.Event()
        release = threading.Event()

        def generate(_genre):
            started.set()
            if not release.wait(5):
                raise TimeoutError("Test did not release the generator")
            return sample_wav()

        with TestClient(app) as client, patch("app.main.generator.generate", side_effect=generate):
            responses = []

            def request_first_track():
                responses.append(client.post("/api/genres/jazz/tracks"))

            worker = threading.Thread(target=request_first_track)
            worker.start()
            try:
                self.assertTrue(started.wait(5))
                busy = client.post("/api/genres/rock/tracks")
                self.assertEqual(busy.status_code, 503)
                self.assertEqual(busy.headers["retry-after"], "2")
                health = client.get("/healthz")
                self.assertEqual(health.status_code, 200)
                self.assertEqual(health.json(), {"status": "ok"})
            finally:
                release.set()
                worker.join()

            self.assertEqual(responses[0].status_code, 200)
            self.assertEqual(client.post("/api/genres/rock/tracks").status_code, 200)
