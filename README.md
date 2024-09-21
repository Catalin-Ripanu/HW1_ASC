# HW1 ASC Report

## Organization

Assignment 1 involves implementing a *Marketplace* that models the *Multiple Producers - Multiple Consumers* problem:

- Producers offer products for sale
- Consumers purchase available products
- Consumers can become producers by removing products from their shopping cart

The implementation utilizes multiple execution threads accessing shared resources, addressing a problem in the domain of Parallel Computing and Multithreading.

## Implementation

### The Consumer Class

- Models the consumer thread
- Uses a cart ID (represented as a list)
- Can add or remove products using a dictionary of functions
- Calls `place_order()` to empty the shopping cart when all operations are complete
- Waits for a specified time if an operation fails
- Thread execution ends when product ordering is activated

### The Producer Class

- Models the producer thread
- Publishes products through the Marketplace
- Receives a list of products to iterate infinitely
- Waits for a specified time after successful publishing
- Waits for a creation-time specified duration if publishing fails

### The Marketplace Class

- Central point of implementation
- Acts as a facade for synchronizing and communicating between threads
- Provides methods called by both consumers and producers
- Maintains:
  - A list of available products
  - A dictionary mapping cart IDs to product lists
  - A dictionary mapping products to their producers (used when consumers remove products from their cart)
  - A dictionary tracking the maximum number of products a producer can publish

### Thread Safety and Synchronization

- Non-thread-safe operations (e.g., increments, decrements) are protected using Locks
- The `publish()`, `add_to_cart()`, and `remove_from_cart()` functions modify producer queue capacities

### Order Placement

- When an order is placed, all products in the cart are displayed to the output stream
- The cart (modeled as a list) is then returned to the consumer

## Resources Used

1. [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
2. [Python RotatingFileHandler Documentation](https://docs.python.org/3/library/logging.handlers.html#logging.handlers.RotatingFileHandler)
3. [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
