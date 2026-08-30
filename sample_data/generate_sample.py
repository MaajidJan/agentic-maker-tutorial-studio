import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sample_dir = Path(__file__).resolve().parent
sample_dir.mkdir(parents=True, exist_ok=True)

img = Image.new("RGB", (800, 600), (18, 24, 38))
draw = ImageDraw.Draw(img)

# Title Header
draw.rectangle([0, 0, 800, 70], fill=(30, 41, 59))
draw.text((20, 25), "MAKER LABS: ARDUINO ULTRASONIC RADAR BUILD", fill=(56, 189, 248))

# Arduino Uno Board
draw.rounded_rectangle([60, 150, 260, 480], radius=10, fill=(0, 120, 130), outline=(255, 255, 255), width=3)
draw.text((80, 170), "ARDUINO UNO R3", fill=(255, 255, 255))
# USB & Power Jack
draw.rectangle([40, 180, 65, 230], fill=(180, 180, 180))
draw.rectangle([40, 410, 65, 460], fill=(30, 30, 30))
# ATmega328 Chip
draw.rectangle([110, 270, 210, 360], fill=(20, 20, 20), outline=(100, 100, 100))
draw.text((120, 305), "ATmega328P", fill=(200, 200, 200))

# SG90 Servo Motor
draw.rounded_rectangle([340, 160, 480, 320], radius=8, fill=(37, 99, 235), outline=(255, 255, 255), width=2)
draw.ellipse([385, 185, 435, 235], fill=(240, 240, 240))
draw.rectangle([400, 120, 420, 190], fill=(240, 240, 240))
draw.text((355, 270), "SG90 SERVO", fill=(255, 255, 255))

# HC-SR04 Ultrasonic Sensor (Mounted on Servo)
draw.rounded_rectangle([530, 130, 740, 260], radius=8, fill=(16, 149, 193), outline=(255, 255, 255), width=2)
# Two Metal Transducers (Bat Ears)
draw.ellipse([550, 150, 625, 225], fill=(160, 160, 160), outline=(255, 255, 255), width=3)
draw.text((575, 180), "TX", fill=(20, 20, 20))
draw.ellipse([645, 150, 720, 225], fill=(160, 160, 160), outline=(255, 255, 255), width=3)
draw.text((670, 180), "RX", fill=(20, 20, 20))
draw.text((560, 235), "HC-SR04 SONAR", fill=(255, 255, 255))

# Breadboard & Jumper Wires
draw.rounded_rectangle([340, 370, 740, 520], radius=8, fill=(245, 245, 245), outline=(200, 200, 200), width=2)
draw.text((360, 390), "SOLDERLESS BREADBOARD (POWER & SIGNALS)", fill=(50, 50, 50))

# Jumper Wires (Colored Lines)
draw.line([(260, 210), (340, 210)], fill=(239, 68, 68), width=3) # VCC (Red)
draw.line([(260, 230), (340, 230)], fill=(30, 30, 30), width=3)   # GND (Black)
draw.line([(260, 250), (340, 250)], fill=(245, 158, 11), width=3) # PWM Signal (Orange)
draw.line([(480, 210), (530, 210)], fill=(34, 197, 94), width=3)  # Echo (Green)
draw.line([(480, 230), (530, 230)], fill=(56, 189, 248), width=3) # Trig (Blue)

# Sonar Radar Waves Annotation
draw.arc([680, 90, 780, 270], start=300, end=60, fill=(56, 189, 248), width=3)
draw.arc([710, 60, 830, 300], start=300, end=60, fill=(56, 189, 248), width=2)
draw.text((540, 80), "40kHz Ultrasonic Echo Wave >>>", fill=(56, 189, 248))

img.save(sample_dir / "arduino_radar.jpg", "JPEG", quality=95)
print("Created sample_data/arduino_radar.jpg")
