from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from .models import Transaction
from .utils import verify_payment

def verify_zarinpal(request):
    print("yes...!")
    authority = request.GET.get("Authority")
    status = request.GET.get("Status")
    if status != "OK":
        return HttpResponse("پرداخت لغو شد.")

    tx = Transaction.objects.filter(authority=authority, status="PENDING").first()
    if not tx:
        return HttpResponse("تراکنش یافت نشد.")

    if verify_payment(authority, tx.amount, settings.ZARINPAL_MERCHANT_ID):
        tx.status = "SUCCESS"
        tx.user.balance += tx.amount
        tx.user.save()
        tx.save()
        return HttpResponse("✅ پرداخت با موفقیت انجام شد. کیف پول شما شارژ شد.")
    else:
        tx.status = "FAILED"
        tx.save()
        return HttpResponse("❌ پرداخت ناموفق بود.")
