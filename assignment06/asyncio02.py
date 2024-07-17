#example of an asynchronous tierator withasync for loop
import asyncio

#define an asynchronous iterator
class AsyncIterator():
    #constructor, define some state
    def __init__(self):
        self.counter = 0

    #create an instance of the iterator
    def __aiter__(self):
        return self
    
    #return the next awaitable
    async def __anext__(self):
        #check for no futher  items
        if self.counter >= 10:
            raise StopAsyncIteration
        #increment the counter
        self.counter += 1 
        #simulate work 
        await asyncio.sleep(1)
        #retrun the countter value
        return self.counter
    
#main coroutine
async def main():
    #loop over async iterator with async for loop
    async for item in AsyncIterator():
        print(item)

#execute the asyncio program
asyncio.run(main())