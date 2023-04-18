"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock, currentThread
import unittest
import logging
from logging.handlers import RotatingFileHandler
from .product import Product


class TestMarketplace(unittest.TestCase):
    """
    Class that represents the test unit of Marketplace.
    """

    def setUp(self):
        """
        Used for creating a Marketplace object instantiation
        """
        self.marketplace = Marketplace(15)
        self.assertEqual(
            self.marketplace.queue_size_per_producer, 15, "wrong queue size"
        )

    def test_register_producer(self):
        """
        Used for testing the register_producer() method
        """
        self.assertEqual(self.marketplace.register_producer(), 0, "wrong producer id")

    def test_publish(self):
        """
        Used for testing the publish() method
        """
        producer = self.marketplace.register_producer()
        self.assertTrue(
            self.marketplace.publish(producer, Product("Indonezia", 1)),
            "wrong return value for publish()",
        )
        i = 0
        while i < self.marketplace.queue_size_per_producer - 1:
            self.marketplace.publish(producer, Product("Linden", 9))
            i += 1
        self.assertFalse(
            self.marketplace.publish(producer, Product("Indonezia", 1)),
            "wrong limit size",
        )
        self.assertTrue(
            self.marketplace.publish(
                self.marketplace.register_producer(), Product("Indonezia", 1)
            ),
            "wrong return value for publish()",
        )

    def test_new_cart(self):
        """
        Used for testing the new_cart() method
        """
        self.assertEqual(self.marketplace.new_cart(), 0, "wrong cart id value")

    def test_add_to_cart(self):
        """
        Used for testing the add_cart() method
        """
        self.marketplace.publish(
            self.marketplace.register_producer(), Product("Indonezia", 1)
        )
        self.assertFalse(
            self.marketplace.add_to_cart(
                self.marketplace.new_cart(), Product("Linden", 9)
            ),
            "wrong return value for add_to_cart()",
        )
        self.assertTrue(
            self.marketplace.add_to_cart(
                self.marketplace.new_cart(), Product("Indonezia", 1)
            ),
            "wrong return value for add_to_cart()",
        )

    def test_remove_from_cart(self):
        """
        Used for testing the remove_from_cart() method
        """
        producer = self.marketplace.register_producer()
        cart = self.marketplace.new_cart()
        self.marketplace.publish(producer, Product("Indonezia", 1))
        self.marketplace.publish(producer, Product("Linden", 9))
        self.marketplace.add_to_cart(cart, Product("Linden", 9))
        self.assertNotEqual(
            self.marketplace.marketplace_products[0],
            Product("Linden", 9),
            "remove failed",
        )
        self.marketplace.remove_from_cart(cart, Product("Linden", 9))
        self.assertEqual(
            self.marketplace.marketplace_products[0],
            Product("Indonezia", 1),
            "add failed",
        )
        return cart

    def test_place_order(self):
        """
        Used for testing the place_order() method
        """
        cart = self.test_remove_from_cart()
        self.marketplace.place_order(cart)
        self.assertEqual(
            self.marketplace.consumer_carts[cart], [], "place_order failed"
        )


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
        file_handler = RotatingFileHandler(
            "marketplace.log",
            mode="a",
            maxBytes=1000,
            backupCount=10,
            encoding="utf-8",
            delay=False,
        )
        self.num_carts = 0
        self.queue_size_per_producer = queue_size_per_producer
        self.marketplace_products = []
        self.consumer_carts = {}
        self.producers_products = {}
        self.producers_queue_size = {}
        self.lock_dict = {
            "safe_print": Lock(),
            "producer_register_lock": Lock(),
            "publish_lock": Lock(),
            "add_cart_lock": Lock(),
            "inc_size_lock": Lock(),
        }

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.lock_dict["producer_register_lock"]:
            current_id = len(self.producers_queue_size)
            self.producers_queue_size[current_id] = 0
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
        with self.lock_dict["publish_lock"]:
            if self.producers_queue_size[int(producer_id)] >= self.queue_size_per_producer:
                return False
            self.marketplace_products = [*self.marketplace_products, product]
            self.producers_queue_size[int(producer_id)] += 1

            self.producers_products[(product.name, product.price)] = int(producer_id)
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        with self.lock_dict["add_cart_lock"]:
            curr_id = self.num_carts
            self.num_carts += 1
            self.consumer_carts[curr_id] = []
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
        with self.lock_dict["add_cart_lock"]:
            if product not in self.marketplace_products:
                return False
            producer = self.producers_products[(product.name, product.price)]
            self.producers_queue_size[producer] -= 1
            self.marketplace_products.remove(product)
            self.consumer_carts[cart_id] = [*self.consumer_carts[cart_id], product]
        return True

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        old_prod = self.consumer_carts[cart_id].pop(
            self.consumer_carts[cart_id].index(product)
        )
        with self.lock_dict["inc_size_lock"]:
            self.marketplace_products = [*self.marketplace_products, old_prod]
            producer = self.producers_products[(old_prod.name, old_prod.price)]
            self.producers_queue_size[producer] += 1

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        list_of_prod = self.consumer_carts[cart_id]
        self.consumer_carts[cart_id] = []
        for product in list_of_prod:
            with self.lock_dict["safe_print"]:
                print("%s bought %s" % (currentThread().getName(), product))
        return list_of_prod
