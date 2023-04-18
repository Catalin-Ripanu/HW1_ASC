"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock, currentThread


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.num_carts = 0
        self.queue_size_per_producer = queue_size_per_producer
        self.marketplace_products = []
        self.consumer_carts = {}
        self.producers_products = {}
        self.producers_queue_size = {}
        self.safe_print = Lock()
        self.producer_register_lock = Lock()
        self.publish_lock = Lock()
        self.add_cart_lock = Lock()
        self.inc_size_lock = Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        self.producer_register_lock.acquire()
        current_id = len(self.producers_queue_size)
        self.producers_queue_size[current_id] = 0
        self.producer_register_lock.release()
        self.producers_products[None] = current_id
        return current_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        self.publish_lock.acquire()
        if self.producers_queue_size[int(producer_id)] >= self.queue_size_per_producer:
            self.publish_lock.release()
            return False
        self.marketplace_products = [*self.marketplace_products, product]
        self.producers_queue_size[int(producer_id)] += 1

        self.producers_products[product] = int(producer_id)
        self.publish_lock.release()
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.add_cart_lock.acquire()
        curr_id = self.num_carts
        self.num_carts += 1
        self.consumer_carts[curr_id] = []
        self.add_cart_lock.release()
        return curr_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        self.add_cart_lock.acquire()
        if product not in self.marketplace_products:
            self.add_cart_lock.release()
            return False
        producer = self.producers_products[product]
        self.producers_queue_size[producer] -= 1
        self.marketplace_products.remove(product)
        self.consumer_carts[cart_id] = [*self.consumer_carts[cart_id], product]
        self.add_cart_lock.release()
        return True

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.consumer_carts[cart_id].remove(product)
        self.inc_size_lock.acquire()
        self.marketplace_products = [*self.marketplace_products, product]
        producer = self.producers_products[product]
        self.producers_queue_size[producer] += 1
        self.inc_size_lock.release()

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        list_of_prod = self.consumer_carts[cart_id]
        self.consumer_carts[cart_id] = []
        for product in list_of_prod:
            self.safe_print.acquire()
            print("{} bought {}".format(currentThread().getName(), product))
            self.safe_print.release()
