import time
import asyncio
from asyncio import Queue
from random import randrange

# we first implement the Customer and Product classes, 
# representing customers and products that need to be checked out. 
# The Product class has a checkout_time attribute, 
# which represents the time required for checking out the product.
class Product:
    def __init__(self, product_name: str, checkout_time: float):
        self.product_name = product_name
        self.checkout_time = checkout_time

class Customer:
    def __init__(self, customer_id: int, products: list[Product]):
        self.customer_id = customer_id
        self.products = products

# we implement a checkout_customer method that acts as a consumer.
# As long as there is data in the queue, this method will continue to loop. 
# During each iteration, it uses a get method to retrieve a Customer instance. 
# 
# If there is no data in the queue, it will wait. 
# 
# After retrieving a piece of data (in this case, a Customer instance), 
# it iterates through the products attribute and uses asyncio.sleep to simulate the checkout process.
# 
# After finishing processing the data, 
# we use queue.task_done() to tell the queue that the data has been successfully processed.
async def checkout_customer(queue: Queue, cashier_number: int, cashier_times: list):
    customer_count = 0  # Initialize the customer count to 0
    total_time = 0  # Initialize total time taken by the cashier

    while True:  # let the cashier always run
        customer: Customer = await queue.get()  # Wait until there's a customer in the queue
        customer_start_time = time.perf_counter()

        customer_count += 1  # Increment the count each time a customer is processed
        print(f"The Cashier_{cashier_number} will checkout Customer_{customer.customer_id}")

        # Calculate total checkout time for this customer
        for product in customer.products:
            product_take_time = round(product.checkout_time, ndigits=2)
            print(f"The Cashier_{cashier_number} will checkout Customer_{customer.customer_id}'s "
                  f"Product_{product.product_name} for {product_take_time:.2f} secs")
            await asyncio.sleep(product_take_time)
            cashier_times[cashier_number] += product_take_time  # Add time to cashier's total

        # Calculate and print the total time taken for this customer
        checkout_time = time.perf_counter() - customer_start_time
        total_time += checkout_time  # Add time taken for this customer to cashier's total time
        print(f"The Cashier_{cashier_number} finished checkout Customer_{customer.customer_id} "
              f"in {checkout_time:.2f} secs")
        print(f"Cashier_{cashier_number} has processed {customer_count} customers.")

        queue.task_done()  # Mark this task as done

    return total_time  # Return the total time the cashier has taken

# we implement the generate_customer method as a factory method for producing customers.
#
# We first define a product series and the required checkout time for each product. 
# Then, we place 0 to 4 products in each customer’s shopping cart.
def generate_customer(customer_id: int) -> Customer:
    all_products = [Product('beef', 1),
                    Product('banana', .4),
                    Product('sausage', .4),
                    Product('diapers', .2)]
    return Customer(customer_id, all_products)

# we implement the customer_generation method as a producer. 
# This method generates several customer instances regularly 
# and puts them in the queue. If the queue is full, the put method will wait.
async def customer_generation(queue: Queue, total_customers: int):
    customer_count = 0
    while customer_count < total_customers:
        new_customer = generate_customer(customer_count)
        print("Waiting to put customer in line....")
        await queue.put(new_customer)
        print(f"Customer_{new_customer.customer_id} put in line...")

        customer_count += 1
        await asyncio.sleep(0.001)  # Add a slight delay for customer arrival

    return customer_count

# Finally, we use the main method to initialize the queue, 
# producer, and consumer, and start all concurrent tasks.
async def main():
    customer_queue = Queue(5)  # Queue size
    customers_start_time = time.perf_counter()

    # Create producer task to add customers to the queue
    customer_producer = asyncio.create_task(customer_generation(customer_queue, 20))

    # List to store total times for each cashier
    cashier_times = [0] * 5

    # Create 5 cashier tasks to process customers
    cashiers = [asyncio.create_task(checkout_customer(customer_queue, i, cashier_times)) for i in range(5)]

    await customer_producer  # Wait for all customers to be generated
    await customer_queue.join()  # Wait for the queue to be fully processed

    # Since cashiers have an infinite loop, we need to cancel them once done
    for cashier in cashiers:
        cashier.cancel()

    print(f"The supermarket process finished with {customer_producer.result()} customers "
          f"in {time.perf_counter() - customers_start_time:.2f} secs")
    
    # Print the total time taken by each cashier
    for i, time_taken in enumerate(cashier_times):
        print(f"Cashier_{i} total checkout time: {time_taken:.1f} secs")

if __name__ == "__main__":
    asyncio.run(main())
