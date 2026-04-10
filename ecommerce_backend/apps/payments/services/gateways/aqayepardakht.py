import requests
import logging
from .base import BaseGateway

logger = logging.getLogger(__name__)


class AqaepardakhtGateway(BaseGateway):
    def __init__(self, config: dict):
        super().__init__(config)
        self.pin = self.config.get("pin")
        self.callback_url = self.config.get("callback_url")
        self.sandbox = self.config.get("sandbox")

    def get_create_url(self) -> str:
        return "https://panel.aqayepardakht.ir/api/v2/create"

    def get_verify_url(self) -> str:
        return "https://panel.aqayepardakht.ir/api/v2/verify"

    def get_startpay_url(self, trans_id: str) -> str:
        if self.sandbox:
            return f"https://panel.aqayepardakht.ir/startpay/sandbox/{trans_id}"
        return f"https://panel.aqayepardakht.ir/startpay/{trans_id}"

    def create(self, amount: int, description: str = None, **kwargs) -> dict:
        data = {
            "pin": self.pin,
            "amount": int(amount),
            "callback": self.callback_url,
            "description": description
        }

        try:
            response = requests.post(self.get_create_url(), data=data)
            result = response.json()
            logger.error(result)

            if response.status_code == 200 and result.get("status") == "success":
                trans_id = result.get("transid")
                return {
                    "is_success": True,
                    "url": self.get_startpay_url(trans_id),
                    "transaction_id": trans_id,
                    "message": "Success",
                    "raw_data": result
                }

            return {
                "is_success": False,
                "message": result.get("message", "Error from gateway"),
                "error_code": result.get("code"),
                "raw_data": result
            }

        except Exception as e:
            logger.error(f"AqaePardakht Create Error: {str(e)}")
            return {"is_success": False, "message": "Connection error"}

    def callback(self, request) -> dict:
        data = request.POST if request.method == "POST" else request.GET
        status = data.get("status")
        trans_id = data.get("transid")
        tracking_number = data.get("tracking_number")

        return {
            "is_success": status == "1",
            "transaction_id": trans_id,
            "reference_id": tracking_number,
            "status_code": status,
            "raw_data": dict(data)
        }

    def verify(self, transaction_id: str, amount: str) -> dict:
        data = {
            "pin": self.pin,
            "amount": amount,
            "transid": transaction_id
        }

        try:
            response = requests.post(self.get_verify_url(), data=data)
            result = response.json()
            if response.status_code == 200 and result.get("status") == "success":
                return {
                    "is_success": True,
                    "transaction_id": result.get('transaction_id'),
                    "raw_data": result
                }

            return {
                "is_success": False,
                "message": result.get("message", "Verification failed"),
                "raw_data": result
            }

        except Exception as e:
            logger.error(f"AqaePardakht Verify Error: {str(e)}")
            return {"is_success": False, "message": "Connection error during verification"}