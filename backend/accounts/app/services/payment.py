import stripe

from app.core import settings
from app.models import User
from app.repositories import BalanceRepository


class PaymentService:
    def __init__(self, balance_repository: BalanceRepository) -> None:
        self.stripe = self._get_stripe_client()
        self.currency = "usd"
        self.payment_method_types = ["card"]
        self.balance_repository = balance_repository

    def _get_stripe_client(self) -> stripe:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe

    def create_customer(self, user: User) -> dict:  # CustomerScheme
        customer = self.stripe.Customer.create(id=user.id, email=user.email)
        return customer

    def create_payment_intent(
        self, amount: int, customer_id: str, currency: str
    ) -> dict:  # PaymentIntentScheme
        payment_intent = self.stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=customer_id,
            payment_method_types=self.payment_method_types,
            description="Payment for user",
        )
        return payment_intent

    async def payment_intent_confirm(
        self, payment_intent: dict
    ):  # PaymentIntentScheme
        balance = await self.balance_repository.get_user_balance_by_currency(
            payment_intent.customer, payment_intent.currency
        )
        balance.amount += payment_intent.amount
        await self.balance_repository.update_balance(balance)

    def get_event(self, payload: dict, sig_header: str) -> dict:  # EventScheme
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            # Invalid payload
            print(f"ValueError: {e}")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print(f"SignatureVerificationError: {e}")
