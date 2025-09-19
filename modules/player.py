import os
import sys
import contextlib
from playsound import playsound

@contextlib.contextmanager
def suppress_alsa_errors():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

def play_response(filename="response.mp3"):
    with suppress_alsa_errors():
        try:
            playsound(filename)
        except Exception as e:
            print(f"❌ 재생 오류: {e}")
