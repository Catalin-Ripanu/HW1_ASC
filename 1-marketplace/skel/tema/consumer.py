"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.functions = {
            "remove": self.marketplace.remove_from_cart,
            "add": self.marketplace.add_to_cart,
        }
        self.retry_wait_time = retry_wait_time

    def run(self):
        """
        Creates a new cart and then performs the specified operations on it.
        If the operation fails, the consumer sleeps 'retry_wait_time' seconds.
        When all the operations have been done, the consumer places the cart's order.
        """
        for _, cart in enumerate(self.carts):
            cart_id = self.marketplace.new_cart()
            for _, operation in enumerate(cart):
                quantity = operation["quantity"]
                while quantity > 0:
                    result = self.functions[operation["type"]](
                        cart_id, operation["product"]
                    )
                    if result or result is None:
                        quantity -= 1
                    else:
                        sleep(self.retry_wait_time)
            self.marketplace.place_order(cart_id)
