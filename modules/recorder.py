import webrtcvad
import pyaudio
import wave
import os
import sys
import contextlib

@contextlib.contextmanager
def suppress_alsa_errors():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

def record_audio(filename="input.wav"):
    vad = webrtcvad.Vad(2)
    with suppress_alsa_errors():
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000,
                            input=True, frames_per_buffer=320)

        print("🎤 소리 감지 중... 말하면 녹음이 시작됩니다")

        frames = []
        triggered = False
        silence_count = 0

        try:
            while True:
                frame = stream.read(320, exception_on_overflow=False)
                is_speech = vad.is_speech(frame, 16000)

                if is_speech:
                    if not triggered:
                        print("🎙️ 녹음 시작!")
                        triggered = True
                    frames.append(frame)
                    silence_count = 0
                elif triggered:
                    frames.append(frame)
                    silence_count += 1
                    if silence_count > 20:
                        print("🛑 녹음 종료")
                        break

        except Exception as e:
            print(f"❌ 녹음 오류: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

        if frames:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(frames))
            wf.close()
        else:
            print("⚠️ 녹음된 음성이 없습니다.")
