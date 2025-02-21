import json
import time
from typing import Dict, List, Optional

import httpx
import ollama
from pydantic import BaseModel, Field


class ATCNumbers(BaseModel):
    Csgn: Optional[str] = Field(None, description="Aircraft Callsign")
    Rway: Optional[str] = Field(None, description="Runway Number")
    Altd: Optional[str] = Field(None, description="Altitude (feet MSL)")
    FLvl: Optional[str] = Field(None, description="Flight Level (FLxxx)")
    Hdng: Optional[str] = Field(None, description="Heading (degrees)")
    VORr: Optional[str] = Field(None, description="VOR Radial Direction")
    Freq: Optional[str] = Field(None, description="Frequency (e.g., 118.7)")
    ASpd: Optional[str] = Field(None, description="Airspeed (knots)")
    Dist: Optional[str] = Field(None, description="Distance (nautical miles)")
    Squk: Optional[str] = Field(None, description="Transponder Code (Squawk)")
    TZlu: Optional[str] = Field(None, description="Standard Time (Zulu)")
    Amtr: Optional[str] = Field(None, description="Altimeter Setting")
    Wdir: Optional[str] = Field(None, description="Wind Direction")
    Wspd: Optional[str] = Field(None, description="Wind Speed (knots)")
    Tmpr: Optional[str] = Field(None, description="Temperature (°C)")
    DewP: Optional[str] = Field(None, description="Dew Point (°C)")


class ATCAnalysis(BaseModel):
    pune: str = Field(..., description="Improved, standardized version of the message")
    intentions: Dict[str, bool] = Field(..., description="Communication intentions")
    numbers: ATCNumbers = Field(..., description="Extracted numerical values")


def parse_atc_blocks(content: str) -> List[Dict]:
    """Parse the entire content into a list of message blocks."""
    lines = content.splitlines()
    blocks = []
    current_block_lines = []
    for line in lines:
        if line.strip() == "":
            # Skip empty lines
            continue
        if line.startswith("{") and current_block_lines:
            # Start of a new block; save the previous one
            blocks.append("\n".join(current_block_lines))
            current_block_lines = [line]
        else:
            current_block_lines.append(line)
    if current_block_lines:
        blocks.append("\n".join(current_block_lines))
    return blocks


def parse_atc_block(block: str) -> Dict:
    """Parse an ATC communication block into its components."""
    lines = block.strip().split("\n")
    result = {}

    # Map of field names to their line prefixes
    field_prefixes = {
        "ORIG": "ORIG:",
        "PROC": "PROC:",
        "NUMC": "NUMC:",
        "PUNC": "PUNC:",
        "PUNE": "PUNE:",
        "NOTE": "NOTE:",
    }

    current_field = None
    for line in lines:
        line = line.strip()
        if line.startswith("{"):
            # Handle header line separately
            current_field = "header"
            result["header"] = line  # Preserve the entire line including '{' and '}'
        else:
            for field, prefix in field_prefixes.items():
                if line.startswith(prefix):
                    current_field = field
                    content = line[len(prefix) :].strip()
                    result[field] = content
                    break
            else:
                if current_field:
                    # Append to the current field
                    result[current_field] += "\n" + line

    # Validate required fields
    required_fields = {"header", "ORIG"}
    missing_fields = required_fields - set(result.keys())
    if missing_fields:
        print(f"Warning: Missing required fields: {missing_fields}")
        print(f"Current block:\n{block}")
        return {}

    # Extract speaker and listener from the header
    speaker_identifier = extract_speaker_identifier_from_header(result["header"])
    result.update(speaker_identifier)

    # Debug print
    print("\nParsed message:")
    print(result)

    return result


def extract_callsign_from_header(header: str) -> str:
    """Extract airline and number from header callsign."""
    # Common airline codes
    airline_codes = {
        "AAL": "American",
        "COA": "Continental",
        "DAL": "Delta",
        "EAL": "Eastern",
        "PAA": "Clipper",
        "MTR": "Metro",
        "ASA": "ASEA",
        "CPL": "Chaparral",
        "BAW": "Speedbird",
        "UAL": "United",
        "TWA": "TWA",
        "MEP": "Midex",
        "MID": "Midway",
        "MXA": "Mexicana",
        "UPS": "UPSCO",
        "FDX": "Express",
        "MSE": "Air Shuttle",
        "EEC": "Hustler",
        "TAC": "Thai-Air",
        "DLH": "Lufthansa",
        "AWE": "Cactus",
        "NWA": "Northwest",
        "SWA": "Southwest",
    }

    # Try to find airline code and number in header
    for code, name in airline_codes.items():
        if code in header:
            # Find the number that follows the code
            parts = header.split(code)
            if len(parts) > 1:
                number = "".join(filter(str.isdigit, parts[1].split("__")[0]))
                if number:
                    return f"{name} {number}"
    return ""


def extract_speaker_identifier_from_header(header: str) -> Dict[str, str]:
    """Extract speaker and listener callsigns from header."""
    # Header format: {session_id speaker_turn speaker_identifier start_time end_time}
    # Example: {dca_d1_1 1 dca_d1_1__DR1-1__DAL209__00_01_03 63.040 66.010}
    header_content = header.strip("{}")
    parts = header_content.split()
    if len(parts) < 3:
        return {"speaker": "", "listener": ""}
    speaker_identifier = parts[2]

    # The speaker_identifier is the third field
    # It can have multiple '__', e.g., 'dca_d1_1__DR1-1__DAL209__00_01_03'
    identifier_parts = speaker_identifier.split("__")
    if len(identifier_parts) >= 3:
        # Assuming format: session_info__speaker__listener__extra_info
        speaker_callsign = identifier_parts[1]
        listener_callsign = identifier_parts[2]
    elif len(identifier_parts) == 2:
        speaker_callsign = identifier_parts[0]
        listener_callsign = identifier_parts[1]
    else:
        speaker_callsign = ""
        listener_callsign = ""

    return {"speaker": speaker_callsign, "listener": listener_callsign}


def determine_speaker_role(speaker_callsign: str) -> str:
    """Determine the role of the speaker (ATC or Pilot) based on the callsign pattern."""
    # List of known airline designators (add more as needed)
    airline_designators = {
        "AAL",
        "UAL",
        "DAL",
        "SWA",
        "NWA",
        "ASA",
        "FFT",
        "BAW",
        "KLM",
        "AFR",
        "DLH",
        "QFA",
        "JBU",
        "VRD",
        "KAL",
        "ANA",
        "EIN",
        "IBE",
        "UAE",
        "CPA",
        "CCA",
        "QTR",
        "SIA",
        "ACA",
        "BAW",
        "GLO",
        "HAL",
        "WJA",
        "VIR",
        "EZY",
        "RYR",
        "NKS",
        "ASA",
        "FDX",
        "UPS",
    }

    # Check if the speaker_callsign starts with any known airline designator
    if any(
        speaker_callsign.upper().startswith(designator)
        for designator in airline_designators
    ):
        return "Pilot"
    else:
        return "ATC"


def analyze_atc_message(
    message: Dict, conversation_history: List[Dict] = None, max_retries: int = 3
) -> ATCAnalysis:
    """Use Ollama to analyze ATC message and generate PUNE and NOTE sections."""

    if conversation_history is None:
        conversation_history = []

    # Create Ollama client with custom endpoint
    client = ollama.Client(host="http://localhost:11435")

    # Extract callsign from header
    callsign = extract_callsign_from_header(message["header"])
    # Extract speaker and listener callsigns
    speaker_callsign = message.get("speaker", "")
    listener_callsign = message.get("listener", "")

    # Determine speaker role based on callsign patterns
    speaker_role = determine_speaker_role(speaker_callsign)

    # Add to context
    context_prompt = f"Callsign from header: {callsign}\n" if callsign else ""
    context_prompt += (
        f"Speaker from header: {speaker_callsign}\n" if speaker_callsign else ""
    )
    context_prompt += (
        f"Listener from header: {listener_callsign}\n" if listener_callsign else ""
    )
    context_prompt += f"Speaker role: {speaker_role}\n"

    system_message = {
        "role": "system",
        "content": """You are an expert in Air Traffic Control (ATC) communications analysis.

Your task is to:

1. Take the PUNC format and improve it into PUNE format following standard ATC communication style:
   - Use proper aviation punctuation and spacing
   - Format numbers according to ATC standards
   - Maintain clear and concise communication style
   Example:
   PUNC: "Delta 2 0 9 turn left ah ah heading 2 8 0."
   PUNE: "Delta 209, turn left heading 280."

2. Analyze the communication flow and context to determine the intentions behind the message.

**Role Identification:**

- The `Speaker role` is provided: it can be **Pilot** or **ATC**.
- Use this information to determine the speaker's role in the communication.

**Intention Labels:**

- For **Pilot** messages, the following intentions might apply:
  - "PSC": Pilot starts contact to ATC.
  - "PSR": Pilot starts contact to ATC with reported info.
  - "PRP": Pilot reports information.
  - "PRQ": Pilot issues requests.
  - "PRB": Pilot readback.
  - "PAC": Pilot acknowledgment.
  - "END": Pilot signaling the end of exchange.
- For **ATC** messages, the following intentions might apply:
  - "ASC": ATC starts contact to pilot.
  - "AGI": ATC gives instruction.
  - "ACR": ATC corrects pilot's readback.
  - "END": ATC signaling the end of exchange.

**Number Extraction Fields:**

- Extract and fill in the following numerical values from the message:
  - **Csgn**: Aircraft Callsign
  - **Rway**: Runway Number
  - **Altd**: Altitude (feet MSL)
  - **FLvl**: Flight Level (FLxxx)
  - **Hdng**: Heading (degrees)
  - **VORr**: VOR Radial Direction
  - **Freq**: Frequency (e.g., 118.7)
  - **ASpd**: Airspeed (knots)
  - **Dist**: Distance (nautical miles)
  - **Squk**: Transponder Code (Squawk)
  - **TZlu**: Standard Time (Zulu)
  - **Amtr**: Altimeter Setting
  - **Wdir**: Wind Direction
  - **Wspd**: Wind Speed (knots)
  - **Tmpr**: Temperature (°C)
  - **DewP**: Dew Point (°C)

**Instructions:**

- Use the `Speaker role` to set the appropriate intentions.
- Only mark intentions relevant to the current message as `true`.
- Extract the numerical values mentioned in the message and fill in the corresponding fields.
- If a value is not present in the message, leave the field empty.

**Follow ATC communication standards:**

- Use commas to separate phrases.
- Group numbers appropriately (callsigns, headings, altitudes).
- Use proper aviation terminology.
- Maintain clear, standardized formatting.

**Important Callsign Rules:**

- Always include the full airline name with the number (e.g., "Delta 209" not just "209").
- Common airline codes:
  - **DAL**/**Delta** → "Delta"
  - **AAL**/**American** → "American"
  - **UAL**/**United** → "United"
  - **SWA**/**Southwest** → "Southwest"
- Format callsigns consistently in both PUNE and numbers sections.
- Extract callsign from both the message and the header.
""",
    }

    # Add context from previous messages
    context_prompt += "Previous messages in this exchange:\n"
    for prev_msg in conversation_history:
        context_prompt += f"- {prev_msg['ORIG']}\n"
    context_prompt += "\nCurrent message to analyze:\n"

    # Construct the analysis request
    analysis_prompt = {
        "role": "user",
        "content": f"""{context_prompt}
Original: {message["ORIG"]}
Processed: {message["PROC"]}
Numeric: {message["NUMC"]}
Punctuated: {message["PUNC"]}

Return ONLY a JSON object with this exact structure (no explanation text, no markdown):
{{
    "pune": "standardized aviation format",
    "intentions": {{
        "PSC": false,
        "PSR": false,
        "PRP": false,
        "PRQ": false,
        "PRB": false,
        "PAC": false,
        "ASC": false,
        "AGI": false,
        "ACR": false,
        "END": false
    }},
    "numbers": {{
        "Csgn": "",
        "Rway": "",
        "Altd": "",
        "FLvl": "",
        "Hdng": "",
        "VORr": "",
        "Freq": "",
        "ASpd": "",
        "Dist": "",
        "Squk": "",
        "TZlu": "",
        "Amtr": "",
        "Wdir": "",
        "Wspd": "",
        "Tmpr": "",
        "DewP": ""
    }}
}}""",
    }

    messages = [system_message, analysis_prompt]

    # Process with streaming and retries
    print(f"\nAnalyzing: {message['ORIG'][:60]}...")

    attempt = 0
    while attempt < max_retries:
        try:
            full_response = ""
            for chunk in client.chat(
                model="llama3.3:70b-instruct-q4_K_M",
                messages=messages,
                stream=True,
            ):
                if chunk.message.content:
                    full_response += chunk.message.content
                    print(".", end="", flush=True)

            print("\nDone!")
            break

        except (httpx.ReadError, ConnectionError) as e:
            attempt += 1
            if attempt < max_retries:
                wait_time = 2**attempt  # Exponential backoff
                print(f"\nConnection error: {str(e)}")
                print(
                    f"Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
            else:
                print(f"\nFailed after {max_retries} attempts: {str(e)}")
                return ATCAnalysis(
                    pune="",
                    intentions={
                        "PSC": False,
                        "PSR": False,
                        "PRP": False,
                        "PRQ": False,
                        "PRB": False,
                        "PAC": False,
                        "ASC": False,
                        "AGI": False,
                        "ACR": False,
                        "END": False,
                    },
                    numbers=ATCNumbers(),
                )

    # Debug print
    print("\nFull response from LLM:")
    print(full_response)

    try:
        raw_analysis = json.loads(full_response.strip())
        analysis = ATCAnalysis(**raw_analysis)
        return analysis
    except Exception as e:
        print(f"Error parsing response: {str(e)}")
        print(f"Raw response: {full_response}")
        return ATCAnalysis(
            pune="",
            intentions={
                "PSC": False,
                "PSR": False,
                "PRP": False,
                "PRQ": False,
                "PRB": False,
                "PAC": False,
                "ASC": False,
                "AGI": False,
                "ACR": False,
                "END": False,
            },
            numbers=ATCNumbers(),
        )


def format_note_section(analysis: ATCAnalysis) -> str:
    """Format the analysis into the NOTE section format."""
    note = """    - Intention:
"""

    intentions = {
        "PSC": "Pilot starts contact to ATC",
        "PSR": "Pilot starts contact to ATC with reported info",
        "PRP": "Pilot reports information",
        "PRQ": "Pilot issues requests",
        "PRB": "Pilot readback",
        "PAC": "Pilot acknowledge",
        "ASC": "ATC starts contact to pilot",
        "AGI": "ATC gives instruction",
        "ACR": "ATC corrects pilot's readback",
        "END": "Either party signaling the end of exchange",
    }

    for code, desc in intentions.items():
        mark = "[x]" if analysis.intentions.get(code, False) else "[]"
        note += f'        - {mark} "{code}": {desc}.\n'

    note += "\n    - Number1:\n"

    # Get all fields from the Pydantic model
    for field_name, field in ATCNumbers.model_fields.items():
        value = getattr(analysis.numbers, field_name, "")
        desc = field.description
        note += f"        - {field_name}: {value}  # {desc}\n"

    return note


def save_json_analysis(processed_blocks: List[Dict], output_path: str):
    """Save the analysis results as a JSON file."""
    json_output = []

    for block in processed_blocks:
        # Extract relevant information
        analysis = {
            "header": block["header"],
            "original": block["ORIG"],
            "processed": block["PROC"],
            "numeric": block["NUMC"],
            "punctuated": block["PUNC"],
            "pune": block["analysis"].pune,
            "intentions": block["analysis"].intentions,
            "numbers": block["analysis"].numbers.model_dump(),
        }
        json_output.append(analysis)

    # Save to JSON file
    json_path = output_path.replace(".lbs", ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)

    print(f"Saved JSON analysis to {json_path}")


def process_file(input_path: str, output_path: str):
    """Process the entire ATC transcription file with context."""
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Use the new parsing function
    blocks = parse_atc_blocks(content)
    processed_blocks = []
    json_blocks = []
    conversation_history = []

    total_blocks = min(30, len(blocks))
    print(f"\nProcessing {total_blocks} messages...")

    for i, block in enumerate(blocks[:30], 1):
        if not block.strip():
            continue

        print(f"\nMessage {i}/{total_blocks}")

        message = parse_atc_block(block)
        if not message:
            continue

        # Analyze with conversation history
        analysis = analyze_atc_message(message, conversation_history)

        # Store message with its analysis
        message["analysis"] = analysis
        json_blocks.append(message)

        # Add to conversation history
        conversation_history.append(message)

        # Keep history manageable
        if len(conversation_history) > 5:
            conversation_history.pop(0)

        # Format block for .lbs file
        new_block = f"{message['header']}\n"
        new_block += f"ORIG: {message['ORIG']}\n"
        new_block += f"PROC: {message['PROC']}\n"
        new_block += f"NUMC: {message['NUMC']}\n"
        new_block += f"PUNC: {message['PUNC']}\n"
        new_block += f"PUNE: {analysis.pune}\n"
        new_block += "NOTE:\n"
        new_block += format_note_section(analysis)

        processed_blocks.append(new_block)

        # Save progress to both formats
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(processed_blocks))

        # Save JSON analysis
        save_json_analysis(json_blocks, output_path)

        print(f"Saved progress to {output_path}")

    print("\nCompleted! All results saved to:")
    print(f"- LBS file: {output_path}")
    print(f"- JSON file: {output_path.replace('.lbs', '.json')}")


if __name__ == "__main__":
    process_file("dca_proc.lbs", "dca_llm.lbs")
    process_file("dfw_proc.lbs", "dfw_llm.lbs")
    process_file("log_id_proc.lbs", "log_id_llm.lbs")
