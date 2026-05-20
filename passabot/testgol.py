import asyncio
from app.airlines.gol import GolCheckinHandler

class DummyPassenger:
    def __init__(self, full_name):
        self.full_name = full_name

class DummyPayload:
    pnr = "ABC123"
    origin = "GRU"
    destination = "SDU"
    departure_date = "2026-05-20"
    airline = "Gol"
    passengers = [DummyPassenger("João da Silva")]

async def main():
    handler = GolCheckinHandler()
    result = await handler.execute(DummyPayload())
    print(result)

asyncio.run(main())