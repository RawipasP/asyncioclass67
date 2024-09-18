from aiokafka import AIOKafkaProducer
import asyncio

async def send_one():
    producer = AIOKafkaProducer(
        bootstrap_servers='localhost:9092')
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    while True:
        try:
        # Produce message
            pr = await producer.send_and_wait("my_topic", b"Super message")
            print(pr)
            await asyncio.sleep(1)
        except:
            # Wait for all pending messages to be delivered or expire.
            await producer.stop()
            

asyncio.run(send_one())