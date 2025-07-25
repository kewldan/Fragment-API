# Чтобы запустить гифты, нужно создать сессию через файл session.py (все создастся автоматически)
import base64
import io
import json
import logging
import re
from typing import List, Optional, Dict, Any, Union

import aiohttp
import tonutils.client
import tonutils.wallet
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.errors import StargiftUsageLimited
from tonsdk.boc import Cell

MNEMONIC: List[str] = [

]

TONAPI_KEY = ""
FRAGMENT_HASH = ""
FRAGMENT_COOKIES = {
    "stel_token": "",
    "stel_ssid": "",
    "stel_ton_token": ""
}
FRAGMENT_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded"
}


def strip_html_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&nbsp;?", " ", text)
    return text.strip()


def clean_and_filter(obj: Union[Dict, List, str, int, float, None]) -> Union[Dict, List, str, int, float, None]:
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            if k.endswith("_html"):
                continue
            clean_v = clean_and_filter(v)
            new[k] = clean_v
        return new
    if isinstance(obj, list):
        return [clean_and_filter(v) for v in obj]
    if isinstance(obj, str):
        return strip_html_tags(obj)
    return obj


class WalletManager:
    def __init__(self, api_key: str, mnemonic: List[str]):
        self.api_key = api_key
        self.mnemonic = mnemonic
        self.ton_client: Optional[tonutils.client.TonapiClient] = None
        self.wallet = None

    async def init_wallet(self):
        self.ton_client = tonutils.client.TonapiClient(api_key=self.api_key)
        self.wallet, _, _, _ = tonutils.wallet.WalletV4R2.from_mnemonic(  # Replace V4R2 with your wallet's version
            self.ton_client, mnemonic=self.mnemonic
        )

    async def transfer(self, address: str, amount: float, comment: str) -> Dict[str, Any]:
        result = {
            "address": address,
            "amount": amount,
            "comment": comment,
            "success": False,
            "tx_hash": None,
            "error": None
        }
        try:
            tx_hash = await self.wallet.transfer(
                destination=address,
                amount=amount,
                body=comment
            )
            result["success"] = True
            result["tx_hash"] = tx_hash
        except Exception as e:
            result["error"] = str(e)
        return result

    async def close(self):
        if self.ton_client and hasattr(self.ton_client, "_session"):
            await self.ton_client._session.close()


def decode_payload_b64(payload: str) -> str:
    try:
        payload += "=" * (-len(payload) % 4)
        cell = Cell.one_from_boc(base64.b64decode(payload))
        sl = cell.begin_parse()
        return sl.read_string().strip()
    except Exception as e:
        return f"decode_error: {e}"


def decode_payload_b64_premium(payload: str) -> str:
    try:
        payload += "=" * (-len(payload) % 4)
        raw_bytes = base64.b64decode(payload)
        decoded = raw_bytes.decode('utf-8', errors='ignore')
        filtered = ''.join(ch for ch in decoded if 32 <= ord(ch) <= 126 or ch in '\r\n')
        filtered = re.sub(r'\r\n?', '\n', filtered)
        filtered = re.sub(r'[ ]*\n+', '\n\n', filtered).strip()
        idx = filtered.find("Telegram Premium")
        if idx != -1:
            filtered = filtered[idx:]
        return filtered
    except Exception as e:
        return f"decode_error: {e}"


async def buy_stars_logic(login: str, quantity: int, hide_sender: int) -> Dict[str, Any]:
    wm = WalletManager(TONAPI_KEY, MNEMONIC)
    await wm.init_wallet()
    results: Dict[str, Any] = {}
    async with aiohttp.ClientSession(cookies=FRAGMENT_COOKIES, headers=FRAGMENT_HEADERS) as session:
        steps = [
            ("updateStarsBuyState", {"mode": "new", "lv": "false", "dh": "1", "method": "updateStarsBuyState"}),
            ("searchStarsRecipient", {"query": login, "quantity": str(quantity), "method": "searchStarsRecipient"}),
            ("updateStarsPrices", {"stars": "", "quantity": str(quantity), "method": "updateStarsPrices"}),
            ("initBuyStarsRequest", {"recipient": None, "quantity": str(quantity), "method": "initBuyStarsRequest"}),
        ]
        for name, data in steps:
            if name == "initBuyStarsRequest":
                recipient = results["searchStarsRecipient"].get("found", {}).get("recipient")
                if not recipient:
                    break
                data["recipient"] = recipient
            async with session.post(f"https://fragment.com/api?hash={FRAGMENT_HASH}", data=data) as resp:
                raw = await resp.json()
            results[name] = clean_and_filter(raw)
            if name == "searchStarsRecipient" and "found" not in raw:
                await wm.close()
                return clean_and_filter(results)
            if name == "initBuyStarsRequest" and not raw.get("req_id"):
                await wm.close()
                return clean_and_filter(results)
        req_id = results["initBuyStarsRequest"]["req_id"]
        account = ""
        device = {
            "platform": "browser",
            "appName": "telegram-wallet",
            "appVersion": "1",
            "maxProtocolVersion": 2,
            "features": ["SendTransaction",
                         {"name": "SendTransaction", "maxMessages": 4, "extraCurrencySupported": True}]
        }
        data5 = {
            "account": json.dumps(account),
            "device": json.dumps(device),
            "transaction": "1",
            "id": req_id,
            "show_sender": str(hide_sender),
            "method": "getBuyStarsLink"
        }
        async with session.post(f"https://fragment.com/api?hash={FRAGMENT_HASH}", data=data5) as resp5:
            raw5 = await resp5.json()
        results["getBuyStarsLink"] = clean_and_filter(raw5)
        if not raw5.get("ok") or "transaction" not in raw5:
            await wm.close()
            return clean_and_filter(results)
        transfers = []
        for msg in raw5["transaction"].get("messages", []):
            addr = msg["address"]
            if isinstance(msg['amount'], str):
                amount_ton = int(msg["amount"]) / 1e9
            else:
                amount_ton = msg["amount"] / 1e9
            raw_payload = msg.get("payload", "")
            decoded = decode_payload_b64(raw_payload)
            transfers.append(await wm.transfer(addr, amount_ton, decoded))
        results["transfers"] = transfers
    await wm.close()
    return clean_and_filter(results)


async def buy_premium_logic(login: str, months: int, hide_sender: int) -> Dict[str, Any]:
    wm = WalletManager(TONAPI_KEY, MNEMONIC)
    await wm.init_wallet()
    results: Dict[str, Any] = {}
    async with aiohttp.ClientSession(cookies=FRAGMENT_COOKIES, headers=FRAGMENT_HEADERS) as session:
        steps = [
            ("updatePremiumState", {"mode": "new", "lv": "false", "dh": "1", "method": "updatePremiumState"}),
            ("searchPremiumGiftRecipient", {"query": login, "method": "searchPremiumGiftRecipient"}),
            ("initGiftPremiumRequest", {"recipient": None, "months": str(months), "method": "initGiftPremiumRequest"}),
        ]
        for name, data in steps:
            if name == "initGiftPremiumRequest":
                recipient = results["searchPremiumGiftRecipient"].get("found", {}).get("recipient")
                if not recipient:
                    break
                data["recipient"] = recipient
            async with session.post(f"https://fragment.com/api?hash={FRAGMENT_HASH}", data=data) as resp:
                raw = await resp.json()
            results[name] = clean_and_filter(raw)
            if name == "searchPremiumGiftRecipient" and "found" not in raw:
                await wm.close()
                return clean_and_filter(results)
            if name == "initGiftPremiumRequest" and not raw.get("req_id"):
                await wm.close()
                return clean_and_filter(results)
        req_id = results["initGiftPremiumRequest"]["req_id"]
        account = ""
        device = {
            "platform": "browser",
            "appName": "telegram-wallet",
            "appVersion": "1",
            "maxProtocolVersion": 2,
            "features": ["SendTransaction",
                         {"name": "SendTransaction", "maxMessages": 4, "extraCurrencySupported": True}]
        }
        data4 = {
            "account": json.dumps(account),
            "device": json.dumps(device),
            "transaction": "1",
            "id": req_id,
            "show_sender": str(hide_sender),
            "method": "getGiftPremiumLink"
        }
        async with session.post(f"https://fragment.com/api?hash={FRAGMENT_HASH}", data=data4) as resp4:
            raw4 = await resp4.json()
        results["getGiftPremiumLink"] = clean_and_filter(raw4)
        if not raw4.get("ok") or "transaction" not in raw4:
            await wm.close()
            return clean_and_filter(results)
        transfers = []
        for msg in raw4["transaction"].get("messages", []):
            addr = msg["address"]
            amount_ton = msg["amount"] / 1e9
            raw_payload = msg.get("payload", "")
            decoded = decode_payload_b64_premium(raw_payload)
            transfers.append(await wm.transfer(addr, amount_ton, decoded))
        results["transfers"] = transfers
    await wm.close()
    return clean_and_filter(results)


class BuyStarsRequest(BaseModel):
    username: str
    quantity: int
    hide_sender: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v < 50:
            raise ValueError("Quantity must be at least 50")
        return v

    @field_validator("hide_sender")
    @classmethod
    def validate_hide_sender(cls, v):
        if v not in (0, 1):
            raise ValueError("hide_sender must be 0 or 1")
        return v


class BuyPremiumRequest(BaseModel):
    username: str
    months: int
    hide_sender: int

    @field_validator("months")
    @classmethod
    def validate_months(cls, v):
        if v not in (3, 6, 12):
            raise ValueError("months must be one of 3, 6, or 12")
        return v

    @field_validator("hide_sender")
    @classmethod
    def validate_hide_sender_premium(cls, v):
        if v not in (0, 1):
            raise ValueError("hide_sender must be 0 or 1")
        return v


class GiftRequest(BaseModel):
    username: str
    gift_id: int
    num_gifts: int


app = FastAPI()


@app.post("/api/buyStars")
async def handle_buy_stars(data: BuyStarsRequest):
    return await buy_stars_logic(data.username, data.quantity, data.hide_sender)


@app.post("/api/buyPremium")
async def handle_buy_premium(data: BuyPremiumRequest):
    return await buy_premium_logic(data.username, data.months, data.hide_sender)


@app.post("/gifts")
async def send_gifts_endpoint(data: GiftRequest):
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger = logging.getLogger(f"gift-{data.username}")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.addHandler(handler)

    logger.info(f"Начало обработки запроса: {data}")

    async with Client("stars", workdir=".") as client:
        try:
            user = await client.get_chat(data.username)
            logger.debug(f"get_chat вернул: {user}")
            if user.type not in (ChatType.PRIVATE, ChatType.CHANNEL):
                msg = f"Неподходящий тип чата: {user.type}"
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
            logger.info(f"Username @{data.username} валиден, имя: {user.first_name}")
        except HTTPException:
            raise
        except Exception as e:
            msg = f"Не удалось найти или получить данные по @{data.username}: {e}"
            logger.exception(msg)
            raise HTTPException(status_code=404, detail=msg)

        successes = 0
        for i in range(1, data.num_gifts + 1):
            try:
                logger.debug(f"Попытка #{i} отправки gift_id={data.gift_id}")
                result = await client.send_gift(
                    chat_id=data.username,
                    gift_id=data.gift_id,
                    is_private=True
                )
                if not result:
                    raise Exception(f"send_gift вернул False на попытке #{i}")
                successes += 1
                logger.info(f"Успешно отправлено #{i}")
            except StargiftUsageLimited as lim:
                logger.warning(f"Лимит подарков достигнут на попытке #{i}: {lim}")
                break
            except Exception as e:
                logger.exception(f"Ошибка при отправке на попытке #{i}: {e}")
                break

    logs = log_stream.getvalue()
    if successes == data.num_gifts:
        return {"status": "success", "sent": successes, "logs": logs}
    else:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "partial" if successes > 0 else "failed",
                "sent": successes,
                "logs": logs
            }
        )
