import requests
from django.conf import settings

#ZARINPAL_API = "https://api.zarinpal.com/pg/v4/payment"
ZARINPAL_API = "https://sandbox.zarinpal.com/pg/v4/payment"

def request_payment(amount, description, callback_url, merchant_id):
    """درخواست پرداخت جدید"""
    data = {
        "merchant_id": merchant_id,
        "amount": amount,
        "description": description,
        "callback_url": callback_url,
    }
    res = requests.post(f"{ZARINPAL_API}/request.json", json=data).json()
    print(res)
    if res["data"]["code"] == 100:
        authority = res["data"]["authority"]
        #pay_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
        pay_url = f"https://sandbox.zarinpal.com/pg/StartPay/{authority}"
        return pay_url, authority
    return None, None


def verify_payment(authority, amount, merchant_id):
    """تأیید پرداخت"""
    data = {"merchant_id": merchant_id, "amount": amount, "authority": authority}
    res = requests.post(f"{ZARINPAL_API}/verify.json", json=data).json()
    if res["data"]["code"] == 100:
        return True
    return False