
import serial
import csv
import time
from datetime import datetime, timedelta

# --------------------------------
# SERIAL SETTINGS
# --------------------------------

SERIAL_PORT = "COM8"
BAUD_RATE = 115200

# --------------------------------
# COLLECTION SETTINGS
# --------------------------------

NUMBER_OF_READINGS = 2880

# One measurement every 30 seconds
READINGS_PER_SECOND = 1 / 30

# Output filename
FILENAME = "bedroom_24hour_data.csv"

# --------------------------------
# CONNECT TO ARDUINO
# --------------------------------

print("Connecting to MKR WiFi 1010...")

ser = serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=35
)

# Allow Arduino to restart after serial connection
time.sleep(5)

ser.reset_input_buffer()

print("Connected successfully.")

# --------------------------------
# START DATA COLLECTION
# --------------------------------

command = (
    f"{NUMBER_OF_READINGS},"
    f"{READINGS_PER_SECOND:.8f}\n"
)

print("Starting 24-hour data collection...")
ser.write(command.encode("utf-8"))

# --------------------------------
# CREATE CSV FILE
# --------------------------------

with open(FILENAME, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "datetime",
        "elapsed_time_ms",
        "temperature_C",
        "humidity_percent"
    ])

    start_time = datetime.now()

    print("Collection started:", start_time)
    print("Expected completion:", start_time + timedelta(hours=24))

    measurements = 0

    try:

        while measurements < NUMBER_OF_READINGS:

            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                print("Waiting for next measurement...")
                continue

            values = line.split(",")

            # Ignore messages that aren't sensor measurements
            if len(values) != 3:
                continue

            try:

                elapsed = int(values[0])
                temperature = float(values[1])
                humidity = float(values[2])

                # Basic data validity checks
                if not (-10 <= temperature <= 60):
                    continue

                if not (0 <= humidity <= 100):
                    continue

                timestamp = datetime.now()

                writer.writerow([
                    timestamp.isoformat(timespec="seconds"),
                    elapsed,
                    temperature,
                    humidity
                ])

                file.flush()

                measurements += 1

                print(
                    f"{measurements}/{NUMBER_OF_READINGS} | "
                    f"Temperature: {temperature:.2f} C | "
                    f"Humidity: {humidity:.2f}%"
                )

            except ValueError:
                continue

    except KeyboardInterrupt:

        print("Collection manually stopped.")

    finally:

        ser.close()

        print("Serial connection closed.")

        print(
            f"Measurements collected: {measurements}"
        )

        print(
            f"CSV saved as: {FILENAME}"
        )
