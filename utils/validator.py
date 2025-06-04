async def submit_to_validator(client, validator, transaction):
    return await client.send_transaction(transaction)
