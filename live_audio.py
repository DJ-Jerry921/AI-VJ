import sounddevice as sd
import numpy as np

DEVICE_ID = 25
SAMPLE_RATE = 48000
BLOCK_SIZE = 1024

print("AI-VJ Live Audio Engine")
print("=" * 50)
print(f"Listening to device {DEVICE_ID}")
print("Play some music on your computer.")
print("Press Ctrl+C to stop.\n")


def audio_callback(indata, frames, time, status):
    if status:
        print(status)

    rms = np.sqrt(np.mean(indata ** 2))

    level = min(int(rms * 100), 50)

    bar = "█" * level
    empty = " " * (50 - level)

    print(
        f"\rAudio [{bar}{empty}] RMS: {rms:.4f}",
        end="",
        flush=True
    )


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
    