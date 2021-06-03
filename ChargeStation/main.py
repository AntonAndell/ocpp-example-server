import asyncio
import src.server 
if __name__ == '__main__':
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(src.server.run())
    loop.close()