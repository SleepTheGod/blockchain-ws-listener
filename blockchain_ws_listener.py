import websocket
import base64
import hashlib
import os
import struct
import time
import json

# Constants
MAGIC = 0xD9B4BEF9
PROTOCOL_VERSION = 70017
MAX_HEADERS_TO_SEND = 1999
total_headers_count = 0
total_MB_received = 0

# Modify system limits (only relevant if you need to increase the file descriptor limit on Linux)
def modify_system_limits():
    os.system("ulimit -n 100000")

# Optimize Go runtime environment (if relevant)
def optimize_go_runtime():
    os.environ["GOMAXPROCS"] = str(os.cpu_count())
    os.environ["GOGC"] = "20"

# Function to create the payload for requesting block headers
def create_get_headers_payload(start_hash, stop_hash):
    payload = struct.pack("<I", MAX_HEADERS_TO_SEND)
    payload += bytes.fromhex(start_hash)[::-1]  # Convert to little-endian
    payload += bytes.fromhex(stop_hash)[::-1]   # Convert to little-endian
    return payload

# Function to generate WebSocket key
def generate_websocket_key():
    key = os.urandom(16)
    return base64.b64encode(key).decode('utf-8')

# Handle incoming messages from the WebSocket
def on_message(ws, message):
    global total_MB_received, total_headers_count
    # Increment total bytes received
    total_MB_received += len(message)
    total_MB = total_MB_received / (1024 * 1024)  # Convert to MB
    print(f"Total received: {total_MB:.2f} MB")

    # Process the incoming message (assuming it is JSON)
    data = json.loads(message)
    if "headers" in data:
        headers_count = len(data["headers"])
        total_headers_count += headers_count
        print(f"Total headers count: {total_headers_count}")

# Handle errors
def on_error(ws, error):
    print(f"WebSocket error: {error}")

# Handle WebSocket closure
def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed: {close_msg}")

# Send the request for block headers
def request_block_headers(ws, start_hash, stop_hash):
    payload = create_get_headers_payload(start_hash, stop_hash)
    message = {
        "op": "getheaders",
        "payload": payload.hex()  # Send as hex string
    }
    ws.send(json.dumps(message))

# Handle WebSocket opening
def on_open(ws):
    # Send a request for block headers immediately after opening
    start_hash = "00000000000000000000614ab7fdeba141738c63548715a86f371a3883084340"
    stop_hash = "00000000000000000002d1451b9178cdd80b0107ea7754676ea3eb3689c4c962"
    request_block_headers(ws, start_hash, stop_hash)

# Main function to run the WebSocket client
def run_websocket():
    ws_address = "wss://ws.blockchain.info/inv"
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(ws_address,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

# Entry point
if __name__ == "__main__":
    modify_system_limits()
    optimize_go_runtime()
    run_websocket()
