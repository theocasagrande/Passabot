import asyncio

from app.models import CheckinResponse
from app.orchestrator import CheckinOrchestrator

orchestrator = CheckinOrchestrator()


async def process_checkin(payload):
    try:
        result = await asyncio.wait_for(orchestrator.run(payload), timeout=150)
        return CheckinResponse(**result)

    except asyncio.TimeoutError:
        return CheckinResponse(
            status="error",
            checked_in=False,
            boarding_pass=None,
            message="Timeout no check-in",
            detail="A execução excedeu 150 segundos.",
        )

    except Exception as e:
        return CheckinResponse(
            status="error",
            checked_in=False,
            boarding_pass=None,
            message="Erro no check-in",
            detail=str(e),
        )