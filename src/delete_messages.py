import asyncio
import telethon
import dotenv

dotenv.load_dotenv()

import asyncio
import telethon


async def action(
    client: telethon.TelegramClient,
    echat,
    fname,
    ffold,
    ts,
    te,
):
     found   = 0
     deleted = 0
     batch   = []

     async for msg in client.iter_messages(
          echat,
          from_user="me",
          offset_date=te if te else None,
     ):
          if ts and msg.date < ts:
               break

          found += 1
          batch.append(msg.id)

          if len(batch) == 100:
               try:
                    await client.delete_messages(echat, batch)
                    deleted += len(batch)
               except Exception as e:
                    print(f"[WARN] delete failed for batch: {e}")

               batch.clear()
               await asyncio.sleep(0.7)

     if batch:
          try:
               await client.delete_messages(echat, batch)
               deleted += len(batch)
          except Exception as e:
               print(f"[WARN] delete failed for final batch: {e}")
               
     print(f"[INFO]: found {found} messages, deleted {deleted}")