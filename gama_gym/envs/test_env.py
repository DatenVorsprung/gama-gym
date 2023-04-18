import asyncio

def hello():
    with connect("ws://localhost:6868") as websocket:
        websocket.send("Hello world!")
        message = websocket.recv()
        print(f"Received: {message}")

hello()