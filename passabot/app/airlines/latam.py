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
        try:
            cookie_btn = page.locator("#cookies-politics-button")
            await cookie_btn.wait_for(state="visible", timeout=3000)
            await cookie_btn.click()
            #print("Banner de cookies fechado com sucesso.")
        except Exception as e:
            #print(f"Banner de cookies não encontrado ou já fechado: {e}")
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
    
    async def _check_search_error(self, page):
        error_message_locator = page.get_by_text("Não pudemos encontrar sua viagem")
        
        if await error_message_locator.is_visible():
            return "Não pudemos encontrar sua viagem. Verifique o código de reserva e o sobrenome."
        return None
    
    async def _get_availability_info(self, page):
        badge = page.get_by_text("Ainda não disponível").first
        if await badge.is_visible():
            try:
                date_info = await page.locator("p:has-text('disponível'), span:has-text('disponível')").first.inner_text()
                return date_info.strip()
            except:
                return "Check-in ainda não disponível"
        return None
    
    async def _check_system_error(self, page):
        system_error = page.get_by_text("Tivemos um problema")
        if await system_error.is_visible():
            detail = await page.get_by_text("Não foi possível carregar a informação").inner_text()
            return f"Erro de sistema da companhia: {detail}"
        return None

    async def execute(self, payload):

        try:
            pnr = (payload.pnr or "").strip()
            nome = (payload.passengers[0].full_name)
            surname = nome.split()[-1]
            if not pnr:
                raise CheckinError("PNR vazio")
            if not surname:
                raise CheckinError("Sobrenome vazio")
            
            max_retries = 2 # Exemplo de regra de negócio [cite: 84]
            for attempt in range(max_retries):
                browser = None
                try:
                    async with Stealth().use_async(async_playwright()) as p:
                        browser = await p.chromium.launch(headless=False)
                        context = await browser.new_context()
                        page = await context.new_page()
                    
                        await page.goto(self.CHECKIN_URL, wait_until="domcontentloaded")
                        await self._close_cookie_banner(page)
                        await page.wait_for_timeout(3000)

                        title = await page.title()
                        if "access denied" in title.lower():
                            raise CheckinError("Acesso bloqueado pelo site da LATAM")
                        
                        order_field = page.locator("#searchbox-code-box-search-order--text-field")
                        surname_field = page.locator("#searchbox-lastname-box-search-order--text-field")

                        await order_field.wait_for(state="visible")
                        await surname_field.wait_for(state="visible")

                        await order_field.fill(pnr)
                        await surname_field.fill(surname)

                        await page.wait_for_timeout(2500)

                        await surname_field.press("ArrowDown")
                        await page.wait_for_timeout(1250)
                        await surname_field.press("Enter")

                        await page.wait_for_timeout(10000)

                        modal_text = await self._get_modal_text(page)

                        if modal_text:
                            await self._close_modal(page)
                            raise CheckinError(modal_text)
                        
                        error_msg = await self._check_search_error(page)
                        if error_msg:
                            raise CheckinError(error_msg)
                        
                        availability_text = await self._get_availability_info(page)
                        if availability_text:
                            return {
                                "status": "error",
                                "checked_in": False,
                                "boarding_pass": None,
                                "message": "Check-in ainda não disponível",
                                "detail": availability_text
                            }
                        
                        sys_err = await self._check_system_error(page)
                        if sys_err:
                            if attempt < max_retries - 1:
                                continue
                            raise CheckinError(sys_err)

                        return {
                            "status": "success",
                            "checked_in": True,
                            "boarding_pass": None,
                            "message": "Check-in realizado com sucesso",
                            "detail": None,
                        }
                    
                except Exception as e:
                    if attempt == max_retries - 1:
                        return {
                            "status": "error",
                            "message": "Erro no check-in",
                            "detail": str(e)
                        }
                finally:
                    if browser:
                        await browser.close()    
            
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