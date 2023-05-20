import uuid as uuid
from dataclasses import dataclass

from yoomoney import Quickpay, Client, Authorize

from tgbot.config import config


class NoPaymentFound(Exception):
    pass


class NotEnoughMoney(Exception):
    pass


def authorize(client_id, redirect_uri):
    Authorize(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=["account-info",
               "operation-history",
               "operation-details",
               "incoming-transfers",
               "payment-p2p",
               "payment-shop",
               ])


@dataclass
class PaymentYooMoney:
    amount: int
    id: str = None

    def create(self):
        self.id = str(uuid.uuid4())

    def check_payment(self):
        client = Client(config.misc.yoomoney_token)
        history = client.operation_history(label=self.id)

        for operation in history.operations:
            return operation.amount
        else:
            raise NoPaymentFound

    @property
    def invoice(self):
        quickpay = Quickpay(receiver=config.misc.yoomoney_wallet,
                            quickpay_form='shop',
                            targets='Deposit balance',
                            paymentType='SB',
                            sum=self.amount,
                            label=self.id)
        return quickpay.base_url
