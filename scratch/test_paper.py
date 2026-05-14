import asyncio
from dotenv import load_dotenv
load_dotenv()

from main import retrieve_for_paper, _run_paper, state, load_all_indexes

async def run():
    loaded = load_all_indexes()
    if not loaded:
        print("Indexes not loaded!")
        return
    print("Indexes loaded, retrieving chunks...")
    meta_a, meta_b = retrieve_for_paper(state)
    print(f"Retrieved {len(meta_a)} from A and {len(meta_b)} from B")
    await _run_paper("پرچہ بنائیں", meta_a, meta_b)

if __name__ == "__main__":
    asyncio.run(run())
