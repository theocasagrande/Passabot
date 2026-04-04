from app.airlines.gol import GolCheckinHandler
from app.airlines.latam import LatamCheckinHandler
from app.airlines.azul import AzulCheckinHandler

class CheckinOrchestrator:
    def __init__(self):
        self.handlers = {
            "Gol": GolCheckinHandler(),
            "Latam": LatamCheckinHandler(),
            "Azul": AzulCheckinHandler(),
        }

    async def run(self, payload):
        handler = self.handlers.get(payload.airline)

        if not handler:
            raise Exception("Companhia não suportada")

        return await handler.execute(payload)