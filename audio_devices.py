import sounddevice as sd

print("AI-VJ Audio Device Scanner")
print("=" * 50)

devices = sd.query_devices()

print(devices)