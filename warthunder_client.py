# file: warthunder_client.py
import asyncio
import aiohttp
from queue import Queue

class WarThunderClient:
    """
    Активно опрашивает встроенный веб-сервер War Thunder для получения 
    данных о состоянии и событиях.
    """
    def __init__(self, data_queue: Queue):
        self.data_queue = data_queue
        self.state_url = "http://localhost:8111/state"
        self.is_running = True

    async def poll_data_loop(self):
        """Асинхронный цикл для постоянного опроса данных."""
        print("Запущен клиент War Thunder. Ожидание начала сессии в игре...")
        async with aiohttp.ClientSession() as session:
            while self.is_running:
                try:
                    async with session.get(self.state_url) as response:
                        if response.status == 200:
                            data = await response.json(content_type=None)
                            if data and data.get('valid', False):
                                self.data_queue.put(data)
                        else:
                            await asyncio.sleep(1)

                except aiohttp.ClientConnectorError:
                    print("Не удалось подключиться к War Thunder. Убедитесь, что игра запущена и вы находитесь в бою.", end='\r')
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"Произошла ошибка при опросе War Thunder: {e}")
                    await asyncio.sleep(2)
                
                await asyncio.sleep(0.1)