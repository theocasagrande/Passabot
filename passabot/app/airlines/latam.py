from app.airlines.base import BaseCheckinHandler

class LatamCheckinHandler(BaseCheckinHandler):

    async def execute(self, payload):
        raise Exception("Latam ainda não implementado")