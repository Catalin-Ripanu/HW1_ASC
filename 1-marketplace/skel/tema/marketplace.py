"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock, currentThread
import unittest
import logging
import time
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
            maxBytes=750,
            backupCount=10,
            encoding="utf-8",
            delay=False,
        )
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s %(levelname)8s: %(message)s")
        file_handler.setFormatter(formatter)
        logging.Formatter.converter = time.gmtime
        self.logger = logging.getLogger("logger")
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

        # Number of carts in Marketplace
        self.num_carts = 0
        self.queue_size_per_producer = queue_size_per_producer

        # The queue containing all the available products
        self.marketplace_products = []

        # A dictionary of lists each representing a consumer's cart
        self.consumer_carts = {}

        # A dictionary mapping products' names and prices to their producers
        self.producers_products = {}

        # A producer's number of items in the queue
        self.producers_queue_size = {}

        # A dictionary containing all the mandatory locks
        self.lock_dict = {

            # Used in order to synchronize the output stream used by multiple threads
            "safe_print": Lock(),

            # Used to register a producer atomically
            "producer_register_lock": Lock(),

            # Used to add a product in Marketplace's queue atomically
            "publish_lock": Lock(),

            # Used to modify the number of carts
            "add_cart_lock": Lock(),

            # Used to modify a producer's queue size
            "inc_size_lock": Lock(),
        }

    def register_producer(self):
        """
        Returns an id for a producer which calls this procedure
        Each id is the producer's index in the dictionary of queue sizes
        """
        self.logger.info(
            "---Entering in register_producer() method--- \
                          %s",
            currentThread().getName(),
        )
        self.logger.info(
            "Number of carts which are stored in Marketplace: %s", self.num_carts
        )
        self.logger.info("Size of a producer's queue: %s", self.producers_queue_size)

        # A lock is needed because the length of the queue sizes
        # may be changed by another registration, before this one proceeds
        with self.lock_dict["producer_register_lock"]:
            current_id = len(self.producers_queue_size)
            self.producers_queue_size[current_id] = 0
        self.producers_products[None] = current_id
        self.logger.info(
            "The return value of register_producer() method: \
                         %s",
            current_id,
        )
        self.logger.info(
            "---Leaving the register_producer() method--- \
                         %s",
            currentThread().getName(),
        )
        return current_id

    def publish(self, producer_id, product):
        """
        Adds the product created by the producer to the Marketplace.
        Increments the producer's number of products in the queue using
        the dictionary and sets it as the producer of the current product

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        self.logger.info(
            "---Entering in publish() method--- \
                         %s",
            currentThread().getName(),
        )
        self.logger.info("A producer's ID: %s", producer_id)
        self.logger.info("A producer's product: %s", product)

        # A lock is needed because the list 'marketplace_products' is shared
        # between multiple producer threads
        with self.lock_dict["publish_lock"]:
            return_val = False
            if self.producers_queue_size[int(producer_id)] >= self.queue_size_per_producer:
                self.logger.info("The return value of publish() method: %s", return_val)
                self.logger.info(
                    "---Leaving the publish() method--- \
                                 %s",
                    currentThread().getName(),
                )
                return return_val
            self.marketplace_products = [*self.marketplace_products, product]
            self.producers_queue_size[int(producer_id)] += 1
            self.logger.info(
                "Producer's queue current size: %s \
                            with ID %s ",
                self.producers_queue_size[int(producer_id)],
                producer_id,
            )
            self.producers_products[(product.name, product.price)] = int(producer_id)
            return_val = True
        self.logger.info("The return value of publish() method: %s", return_val)
        self.logger.info(
            "---Leaving the publish() method--- \
                         %s",
            currentThread().getName(),
        )
        return return_val

    def new_cart(self):
        """
        Creates a new cart for the consumer.
        Each new cart receives a new ID so that a new entry in
        the dictionary is made

        :returns an int representing the cart_id
        """
        self.logger.info(
            "---Entering in new_cart() method--- \
                         %s",
            currentThread().getName(),
        )

        # The number of carts should be increased atomically
        # 'cart_id' is being used for decreasing the sequential code's size
        with self.lock_dict["add_cart_lock"]:
            curr_id = self.num_carts
            self.num_carts += 1
            self.consumer_carts[curr_id] = []
            self.logger.info("Current ID of a cart: %s", curr_id)
            self.logger.info("Carts from Marketplace: %s", self.consumer_carts)
        self.logger.info(
            "---Leaving the new_cart() method--- \
                         %s",
            currentThread().getName(),
        )
        return curr_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart.
        Decreases the producer's number of products in the queue
        and removes the given product from it's buffer
        The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        self.logger.info(
            "---Entering in add_to_cart() method--- \
                         %s",
            currentThread().getName(),
        )
        self.logger.info("A consumer's cart ID: %s", cart_id)
        self.logger.info("A product added by the consumer: %s", product)

        # A lock is mandatory so that multiple consumers don't try to
        # remove the same product from the list
        # For example, it can be a situation when all the consumers pass
        # the 'if' statement when there is only 1 product left in buffer
        with self.lock_dict["add_cart_lock"]:
            return_val = False
            if product not in self.marketplace_products or (
                    (product.name, product.price) not in self.producers_products
            ):
                self.logger.info(
                    "---Leaving the add_to_cart() method--- \
                                 %s",
                    currentThread().getName(),
                )
                self.logger.info(
                    "The return value of add_to_cart() method: %s", return_val
                )
                return return_val
            producer = self.producers_products[(product.name, product.price)]
            self.logger.info("The product's producer: %s", producer)
            self.producers_queue_size[producer] -= 1
            self.marketplace_products.remove(product)
            self.consumer_carts[cart_id] = [*self.consumer_carts[cart_id], product]
            self.logger.info(
                "---Leaving the add_to_cart() method--- \
                             %s",
                currentThread().getName(),
            )
            self.logger.info("The return value of add_to_cart() method: %s", return_val)
            return_val = True
        return return_val

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.
        Reintroduce it into the list of all Marketplace products
        and increases its producer's queue size.
        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.logger.info(
            "---Entering in remove_from_cart() method--- \
                         %s",
            currentThread().getName(),
        )
        self.logger.info("A consumer's cart ID: %s", cart_id)
        self.logger.info("A product removed by the consumer: %s", product)
        old_prod = self.consumer_carts[cart_id].pop(
            self.consumer_carts[cart_id].index(product)
        )

        # Multiple consumers may try to remove a product
        # which was created by the same producer, thus the increasing
        # of the producer's queue must be atomic.
        with self.lock_dict["inc_size_lock"]:
            self.marketplace_products = [*self.marketplace_products, old_prod]
            producer = self.producers_products[(old_prod.name, old_prod.price)]
            self.producers_queue_size[producer] += 1
            self.logger.info(
                "Producer's queue size after \
                             removing from cart: %s",
                self.producers_queue_size,
            )
            self.logger.info(
                "---Leaving from remove_from_cart() method--- \
                             %s",
                currentThread().getName(),
            )

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        self.logger.info(
            "---Entering in place_order() method--- \
                         %s",
            currentThread().getName(),
        )
        self.logger.info("A consumer's cart ID: %s", cart_id)
        self.logger.info("Cart before order: %s", self.consumer_carts[cart_id])
        list_of_prod = self.consumer_carts[cart_id]
        self.consumer_carts[cart_id] = []
        self.logger.info("Cart after order: %s", self.consumer_carts[cart_id])
        for product in list_of_prod:

            # A lock is used in order not to interleave the printed strings.
            with self.lock_dict["safe_print"]:
                to_print = f"{currentThread().getName()} bought {product}"
                print(to_print)
        self.logger.info("The return value of place_order() method: %s", list_of_prod)
        self.logger.info(
            "---Leaving the place_order() method--- \
                         %s",
            currentThread().getName(),
        )
        return list_of_prod
