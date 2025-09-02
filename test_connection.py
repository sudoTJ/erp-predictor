import httpx
import asyncio

async def test_connection():
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("Testing connection to ERP service...")
            response = await client.get("http://localhost:3001/api/v1/inventory/SKU001/history?days=180")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Got {len(data['history'])} historical records")
                print("Connection test successful!")
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())