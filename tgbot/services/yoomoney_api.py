import uuid as uuid
from dataclasses import dataclass

from yoomoney import Quickpay, Client, Authorize

from tgbot.config import config


class NoPaymentFound(Exception):
    pass


class NotEnoughMoney(Exception):
    pass


def authorize(client_id: str, redirect_uri: str) -> None:
    Authorize(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=[
            "account-info",
            "operation-history",
            "operation-details",
            "incoming-transfers",
            "payment-p2p",
            "payment-shop",
        ],
    )


@dataclass
class PaymentYooMoney:
    amount: int
    id: str = None

    def create(self) -> None:
        self.id = str(uuid.uuid4())

    def check_payment(self) -> float | None:
        client = Client(config.yoomoney.token)
        history = client.operation_history(label=self.id)

        for operation in history.operations:
            return operation.amount
        else:
            raise NoPaymentFound

    @property
    def invoice(self) -> str:
        quick_pay = Quickpay(
            receiver=config.yoomoney.wallet,
            quickpay_form="shop",
            targets="Deposit balance",
            paymentType="SB",
            sum=self.amount,
            label=self.id,
        )
        return quick_pay.base_url
