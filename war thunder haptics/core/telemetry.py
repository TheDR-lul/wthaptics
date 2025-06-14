import asyncio
import aiohttp

class TelemetryPoller:
    def __init__(self, poll_interval_ms: int = 50):
        self.url = "http://localhost:8111/state"
        self.poll_interval = poll_interval_ms / 1000
        self._running = False
        self._callbacks = []

    def add_callback(self, callback):
        self._callbacks.append(callback)

    async def start(self):
        self._running = True
        async with aiohttp.ClientSession() as session:
            while self._running:
                try:
                    async with session.get(self.url) as resp:
                        data = await resp.json()
                        for cb in self._callbacks:
                            cb(data)
                except Exception as e:
                    print(f"[Telemetry] Error: {e}")
                await asyncio.sleep(self.poll_interval)

    def stop(self):
        self._running = False
