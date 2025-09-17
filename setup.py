# 📄 setup.py (패키지 설치용)
from setuptools import setup, find_packages

setup(
    name="pi-voice-assistant",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.3.0",
        "google-cloud-texttospeech>=2.14.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "pytz>=2022.7",
    ],
    author="Your Name",
    description="Raspberry Pi Voice Assistant with Gemini AI",
    python_requires=">=3.8",
)