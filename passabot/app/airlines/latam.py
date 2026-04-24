from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from app.airlines.base import BaseCheckinHandler
from app.utils.errors import CheckinError

class LatamCheckinHandler(BaseCheckinHandler):
    CHECKIN_URL = "https://www.latamairlines.com/br/pt/check-in"

    COOKIE_BUTTON_NAMES = [
        "Aceite todos os cookies",
        "Recusar todos os cookies"
    ]

    MODAL_CLOSE_BUTTON_NAMES = [
        "Ok, entendi",
        "OK, entendi",
        "Ok entendi",
        "Entendi",
    ]

    async def _close_cookie_banner(self, page):
        for name in self.COOKIE_BUTTON_NAMES:
            try:
                btn = page.get_by_role("button", name=name)
                if await btn.count() > 0:
                    await btn.first.click(timeout=1500)
                    return
            except Exception:
                pass

    #ckin-couldnt-find-flights-by-orderId-action

    async def execute(self, payload):
        browser = None

        try:
            pnr = (payload.pnr or "").strip()
            surname = (payload.passengers.full_name)
            print(surname)
            if not pnr:
                raise CheckinError("PNR vazio")
            # if not surname:
            #     raise CheckinError("Sobrenome vazio")

            async with Stealth().use_async(async_playwright()) as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()
            
            await page.goto(self.CHECKIN_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            title = await page.title()

            return {
                "status": "success",
                "checked_in": True,
                "boarding_pass": None,
                "message": "Check-in realizado com sucesso",
                "detail": None,
            }
            
        except Exception as e:
            if browser:
                try:
                    await browser.close()
                except Exception:
                    pass

            return {
                "status": "error",
                "checked_in": False,
                "boarding_pass": None,
                "message": "Erro no check-in",
                "detail": str(e),
            }