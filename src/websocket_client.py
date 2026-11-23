import asyncio
import json
import websockets
from datetime import datetime

# Binance BTC/USDT Public Trade Stream endpoint
BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"

async def stream_live_crypto_ticks():
    print("Connecting to Binance WebSocket stream...")
    async with websockets.connect(BINANCE_WS_URL) as ws:
        print("Connected successfully! Streaming live market ticks:\n" + "-" * 50)
        try:
            while True:
                response = await ws.recv()
                data = json.loads(response)

                # Extract trade execution fields
                timestamp = datetime.fromtimestamp(data['T'] / 1000).strftime('%H:%M:%S')
                price = float(data['p'])
                quantity = float(data['q'])
                is_buyer_maker = data['m']
                side = "SELL" if is_buyer_maker else "BUY"

                print(f"[{timestamp}] {side:4s} | Price: ${price:,.2f} | Size: {quantity:.4f} BTC")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed. Please attempt to reconnect.")

if __name__ == "__main__":
    asyncio.run(stream_live_crypto_ticks())
