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
        
async def checkout_customer(queue: Queue, cashier_number: int):
    cashier_take = {"id" : cashier_number,"customer":0,"time":0}
    while not queue.empty():
        customer: Customer = await queue.get()
        customer_start_time = time.perf_counter()
        cashier_take['customer'] += 1
        print(f"The Cashier_ {cashier_number}"
              f" will checkout Customer_ {customer.customer_id}")
        for product in customer.products:
            if cashier_number ==2:
                product_take_time = 0.1
            else:
                product_take_time = round(product.checkout_time+(0.1*cashier_number), ndigits=2)
                
            print(f"The Cashier_ {cashier_number}"
                  f" will checkout Customer_ {customer.customer_id}"
                  f" Product_ {product.product_name}"
                  f" in {product.checkout_time} secs")
            await asyncio.sleep(product_take_time)
            cashier_take["time"] += product_take_time
        print(f"The Cashier_ {cashier_number}"
              f" finish checkout Customer_ {customer.customer_id}"
              f" in {round(time.perf_counter() - customer_start_time, ndigits=2)} secs")
        
        queue.task_done()
    return cashier_take

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
async def customer_generation(queue: Queue, customers: int):
    customer_count = 0
    while True:
        customers = [generate_customer(the_id)
                     for the_id in range(customer_count,customer_count+customers)]
        for customer in customers:
            print("Waiting to put the customer in line....")
            await queue.put(customer)
            print("Customer put in line....")
        customer_count = customer_count +len(customers)
        await asyncio.sleep(.001)
        return customer_count

# Finally, we use the main method to initialize the queue, 
# producer, and consumer, and start all concurrent tasks.
async def main():
    customer_queue = Queue(10)
    customer_start_time = time.perf_counter()
    async with asyncio.TaskGroup() as group:
        customer_group = group.create_task(customer_generation(customer_queue,10))
        cashiers_group = [group.create_task(checkout_customer(customer_queue,i)) for i in range(5)] 

    print("-"*20)
    for cg in cashiers_group:
        if cg.result():
            cashier = cg.result()
            print(f"The Cashier_ {cashier['id']}"
                  f" took {cashier['customer']} customers"
                  f" time {round(cashier['time'],ndigits=2)} secs")
    if customer_group.result():
        print(f"The supermarket process finished "
            f"{customer_group.result()} customers"
                f"in {round(time.perf_counter() - customer_start_time,ndigits=2)} secs")

    
if __name__ == "__main__":
    asyncio.run(main())