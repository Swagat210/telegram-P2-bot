import uuid
from .config import HOST, MERCHANT_UPI

def generate_order_id():
    return 'ORDER_' + uuid.uuid4().hex[:12].upper()

def create_upi_pay_link(order_id, amount):
    # Create a UPI deep link. Some UPI apps support this format.
    # Real integrations might instead create a QR through a payment gateway.
    # Example: upi://pay?pa=merchant@bank&pn=MyBusiness&tr=ORDER123&am=99.00&cu=INR
    link = f"upi://pay?pa={MERCHANT_UPI}&pn=PremiumShop&tr={order_id}&am={amount:.2f}&cu=INR"
    # Return a web-hosted page URL where the QR will be shown
    pay_page = f"{HOST}/pay/{order_id}"
    return link, pay_page
