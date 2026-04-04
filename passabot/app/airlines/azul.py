from app.airlines.base import BaseCheckinHandler

class AzulCheckinHandler(BaseCheckinHandler):

    async def execute(self, payload):
        raise Exception("Azul ainda não implementado")