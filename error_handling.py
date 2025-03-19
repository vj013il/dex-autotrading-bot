async def safe_execute(self, func, retries=3):
    for _ in range(retries):
        try:
            return await func()
        except Exception as e:
            print(f"Retrying... Error: {e}")
            await asyncio.sleep(1)
    raise Exception("Max retries exceeded")
