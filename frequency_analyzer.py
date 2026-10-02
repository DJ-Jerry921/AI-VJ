import sounddevice as sd
import numpy as np

DEVICE_ID = 25
SAMPLE_RATE = 48000
BLOCK_SIZE = 2048

# Each band keeps its own adaptive reference level
levels = {
    "bass": 0.01,
    "mid": 0.01,
    "high": 0.01
}

SMOOTHING = 0.85


def make_bar(value, width=25):
    value = np.clip(value, 0, 1)
    length = int(value * width)

    return "█" * length + " " * (width - length)


def normalize_band(name, value):
    # Slowly adapt the reference level
    levels[name] = max(
        value,
        levels[name] * 0.995
    )

    normalized = value / (levels[name] + 1e-8)

    return np.clip(normalized, 0, 1)


# Smoothed visual values
smooth_bass = 0
smooth_mid = 0
smooth_high = 0


def audio_callback(indata, frames, time, status):

    global smooth_bass
    global smooth_mid
    global smooth_high

    if status:
        print(status)

    # Stereo -> Mono
    audio = np.mean(indata, axis=1)

    # Remove DC offset
    audio = audio - np.mean(audio)

    # Hann window
    windowed = audio * np.hanning(len(audio))

    # FFT
    spectrum = np.abs(np.fft.rfft(windowed))

    frequencies = np.fft.rfftfreq(
        len(windowed),
        1 / SAMPLE_RATE
    )

    # Frequency bands
    bass_mask = (
        (frequencies >= 20) &
        (frequencies < 250)
    )

    mid_mask = (
        (frequencies >= 250) &
        (frequencies < 4000)
    )

    high_mask = (
        (frequencies >= 4000) &
        (frequencies < 16000)
    )

    # RMS energy inside each frequency band
    bass = np.sqrt(
        np.mean(spectrum[bass_mask] ** 2)
    )

    mid = np.sqrt(
        np.mean(spectrum[mid_mask] ** 2)
    )

    high = np.sqrt(
        np.mean(spectrum[high_mask] ** 2)
    )

    # Adaptive normalization
    bass = normalize_band("bass", bass)
    mid = normalize_band("mid", mid)
    high = normalize_band("high", high)

    # Smooth movement
    smooth_bass = (
        SMOOTHING * smooth_bass
        + (1 - SMOOTHING) * bass
    )

    smooth_mid = (
        SMOOTHING * smooth_mid
        + (1 - SMOOTHING) * mid
    )

    smooth_high = (
        SMOOTHING * smooth_high
        + (1 - SMOOTHING) * high
    )

    print(
        "\r"
        f"BASS [{make_bar(smooth_bass)}] "
        f"MID [{make_bar(smooth_mid)}] "
        f"HIGH [{make_bar(smooth_high)}]",
        end="",
        flush=True
    )


print("AI-VJ Frequency Analyzer V0.2")
print("=" * 60)
print("Listening...")
print("Press Ctrl+C to stop.\n")


try:

    with sd.InputStream(
        device=DEVICE_ID,
        channels=2,
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        callback=audio_callback
    ):

        while True:
            sd.sleep(1000)


except KeyboardInterrupt:

    print("\n\nAI-VJ stopped.")


except Exception as e:

    print(f"\nERROR: {e}")