# Define formatted intention checklist with proper indentation
intention_checklist = """\
    - Intention:
        - [] "PSC": Pilot starts contact to ATC.
        - [] "PSR": Pilot starts contact to ATC with reported info.
        - [] "PRP": Pilot reports information.
        - [] "PRQ": Pilot issues requests.
        - [] "PRB": Pilot readback.
        - [] "PAC": Pilot acknowledge.
        - [] "ASC": ATC starts contact to pilot.
        - [] "AGI": ATC gives instruction.
        - [] "ACR": ATC corrects pilot's readback.
        - [] "END": Either party signaling the end of exchange.

    - Number1:
        - Csgn:  # Aircraft Callsign
        - Rway:  # Runway Number
        - Altd:  # Altitude (feet MSL)
        - FLvl:  # Flight Level (FLxxx)
        - Hdng:  # Heading (degrees)
        - VORr:  # VOR Radial Direction
        - Freq:  # Frequency (e.g., 118.7)
        - ASpd:  # Airspeed (knots)
        - Dist:  # Distance (nautical miles)
        - Squk:  # Transponder Code (Squawk)
        - TZlu:  # Standard Time (Zulu)
        - Amtr:  # Altimeter Setting
        - Wdir:  # Wind Direction
        - Wspd:  # Wind Speed (knots)
        - Tmpr:  # Temperature (°C)
        - DewP:  # Dew Point (°C)
"""


def format_pune(punc_text):
    """Leaves PUNE blank as per request."""
    return "PUNE: "


def process_transcription(file_path, output_path):
    """Reads the transcription file, processes the first 30 entries, and writes the output."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read().strip().split("\n\n")  # Split blocks by empty line

    processed_data = []

    for i, block in enumerate(data[:30]):  # Process first 30 entries
        lines = block.strip().split("\n")

        if len(lines) < 5:
            continue  # Skip malformed entries

        orig_text = lines[1].replace("ORIG:", "").strip()
        proc_text = lines[2].replace("PROC:", "").strip()
        numc_text = lines[3].replace("NUMC:", "").strip()
        punc_text = lines[4].replace("PUNC:", "").strip()

        # Generate new fields
        pune_text = format_pune(punc_text)

        # Reconstruct block with new fields
        new_block = f"{lines[0]}\nORIG: {orig_text}\nPROC: {proc_text}\nNUMC: {numc_text}\nPUNC: {punc_text}\n{pune_text}\nNOTE:\n{intention_checklist}"

        processed_data.append(new_block)

    # Write the modified data to a new file
    with open(output_path, "w", encoding="utf-8") as out_file:
        out_file.write("\n\n".join(processed_data))

    print(f"Processed {min(30, len(data))} entries and saved to {output_path}.")


# Process the transcription files
process_transcription("log_id.lbs", "log_id_proc.lbs")
