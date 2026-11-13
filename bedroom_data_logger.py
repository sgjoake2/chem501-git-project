
import serial
import csv
import time
from datetime import datetime
import os

SERIAL_PORT = "COM8"
BAUD_RATE = 115200

filename = "bedroom_data.csv"

ser = serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=2
)

time.sleep(2)

print("Bedroom data collection started")

file_exists = os.path.exists(filename)

with open(filename, "a", newline="") as file:

    writer = csv.writer(file)

    if not file_exists or os.path.getsize(filename) == 0:
        writer.writerow([
            "datetime",
            "elapsed_time_ms",
            "temperature_C",
            "humidity_percent",
            "pressure_hPa",
            "gas_resistance"
        ])

    try:
        while True:

            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            values = line.split(",")

            if len(values) != 5:
                continue

            try:
                elapsed = int(values[0])
                temp = float(values[1])
                humidity = float(values[2])
                pressure = float(values[3])
                gas = float(values[4])

                if not (-10 <= temp <= 60):
                    continue

                if not (0 <= humidity <= 100):
                    continue

                timestamp = datetime.now().isoformat(
                    timespec="seconds"
                )

                writer.writerow([
                    timestamp,
                    elapsed,
                    temp,
                    humidity,
                    pressure,
                    gas
                ])

                file.flush()

                print(
                    f"Temperature: {temp} °C | "
                    f"Humidity: {humidity}% | "
                    f"Pressure: {pressure} hPa"
                )

            except ValueError:
                continue

    except KeyboardInterrupt:
        print("Collection stopped")

    finally:
        ser.close()
