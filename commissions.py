async def get_priority_fee(self):
    # Adaptive commission through Jito
    response = await self.client.get_recent_prioritization_fees()
    return response[0].prioritization_fee * 1.1  # +10%
