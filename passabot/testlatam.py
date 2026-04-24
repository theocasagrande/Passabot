import asyncio
from app.airlines.latam import LatamCheckinHandler

class DummyPassenger:
    def __init__(self, full_name):
        self.full_name = full_name

class DummyPayload:
    pnr = "ABC123"
    origin = "GRU"
    destination = "LAX"
    departure_date = "2026-05-20"
    airline = "Latam"
    checkin_url = "https://www.latamairlines.com/br/pt/check-in"
    passengers = [DummyPassenger("João da Silva")]

async def main():
    handler = LatamCheckinHandler()
    result = await handler.execute(DummyPayload())
    print(result)

asyncio.run(main())