# HW1_ASC

### Organization

Assignment 1 refers to the implementation of a *Marketplace* which represents the central object of modeling the *Multiple Producers - Multiple Consumers* problem where each producer offers their products for sale, and each consumer purchases the available products, with the mention that a certain consumer can become a producer if they remove a product from their shopping cart.

I consider that the chosen implementation is optimal and natural from the point of view of using multiple execution threads that access shared resources. Also, the assignment proved its usefulness considering that it addresses a problem of a vast domain of interest, namely Parallel Computing and Multithreading.

### Implementation

*The Consumer Class* represents the modeling of the consumer thread which, based on an ID of a cart constructed in the form of a list, can remove or add products using a dictionary containing *functions*. When all operations are fulfilled, the consumer calls the *place_order()* function to empty their shopping cart. In the situation where the current operation fails, the consumer waits for a time that is extracted from the input file. Obviously, the execution of this type of thread ends when the product ordering is activated.

*The Producer Class* represents the modeling of the producer thread that publishes, through the Marketplace, products intended for consumers. Such a thread receives a list of products which it iterates infinitely so that all consumers obtain the desired products. If the publishing operation is successfully fulfilled, the producer waits for a time that is extracted from its own product list. Otherwise, it waits for a time that is given to the thread at creation.

*The Marketplace Class* represents the central point of the implementation as it offers methods that are called by both consumers and producers, in other words, it plays the role of a *facade* that facilitates the synchronization and communication of these threads. This class retains a *list of products* available, a dictionary that associates a certain ID with a certain list of products from a shopping cart, and another dictionary that maps a product with its producer that will be used when a consumer decides to give up the product put in their cart.

To keep track of the maximum number of products that can be published by a producer, a dictionary is used that links the ID of such a thread to the capacity of its product queue (this capacity is modified within the functions *publish()*, *add_to_cart()* and *remove_from_cart()*).

Obviously, all operations that are not thread-safe, such as increments or decrements, are protected using specialized synchronization mechanisms, more precisely *Locks*.

When an order is placed, all products in that cart are displayed to the output stream before the list modeling the cart is returned to the consumer.

### Resources Used

3. https://docs.python.org/3/library/logging.html
4. https://docs.python.org/3/library/logging.handlers.html#logging.handlers.RotatingFileHandler
5. https://docs.python.org/3/howto/logging.html
