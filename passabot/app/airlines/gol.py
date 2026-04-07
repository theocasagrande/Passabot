import traceback

from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from app.airlines.base import BaseCheckinHandler
from app.utils.errors import CheckinError


class GolCheckinHandler(BaseCheckinHandler):
    CHECKIN_URL = "https://b2c.voegol.com.br/check-in/"

    COOKIE_BUTTON_NAMES = [
        "Continue and close",
        "Reject All",
        "Continuar e fechar",
        "Rejeitar tudo",
        "Aceitar todos",
        "Accept All",
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

    async def _get_modal_text(self, page):
        try:
            modal = page.locator("#reserve-not-found")
            if await modal.count() > 0 and await modal.first.is_visible():
                return (await modal.first.inner_text()).strip()
        except Exception:
            pass

        try:
            body = await page.locator("body").inner_text()
            if "check-in do seu voo não está disponível" in body.lower():
                return "O check-in do seu voo não está disponível."
        except Exception:
            pass

        return None

    async def _close_modal(self, page):
        for name in self.MODAL_CLOSE_BUTTON_NAMES:
            try:
                btn = page.get_by_role("button", name=name)
                if await btn.count() > 0 and await btn.first.is_visible():
                    await btn.first.click(timeout=2000)
                    return
            except Exception:
                pass

    async def execute(self, payload):
        browser = None

        try:
            pnr = (payload.pnr or "").strip()
            origin = (payload.origin or "").strip().upper()

            if not pnr:
                raise CheckinError("PNR vazio")
            if not origin:
                raise CheckinError("Origem vazia")

            async with Stealth().use_async(async_playwright()) as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                page.set_default_timeout(15000)

                await page.goto(self.CHECKIN_URL, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)

                title = await page.title()
                if "access denied" in title.lower():
                    raise CheckinError("Acesso bloqueado pelo site da GOL")

                await self._close_cookie_banner(page)

                locator_field = page.locator("#input-locator")
                origin_field = page.locator("#input-departure")

                await locator_field.wait_for()
                await origin_field.wait_for()

                await locator_field.fill(pnr)
                await origin_field.fill(origin)

                await page.wait_for_timeout(2500)

                await origin_field.press("ArrowDown")
                await page.wait_for_timeout(1250)
                await origin_field.press("Enter")

                await page.wait_for_timeout(4000)

                modal_text = await self._get_modal_text(page)

                if modal_text:
                    await self._close_modal(page)
                    raise CheckinError(modal_text)

                await browser.close()
                browser = None

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