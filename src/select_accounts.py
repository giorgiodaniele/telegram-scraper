import telethon
import pandas
import os
import dotenv
import azure_integration

dotenv.load_dotenv()

# Azure
AZURE_ENABLED              = os.environ["AZURE_ENABLED"]
AZURE_STORAGE_ACCOUNT      = os.environ["AZURE_STORAGE_ACCOUNT"]
AZURE_STORAGE_ACCOUNT_BLOB = os.environ["AZURE_STORAGE_ACCOUNT_BLOB"]

async def action(
     client: telethon.TelegramClient, 
     echat,
     fname,
     ffold,
     ts,
     te
):
     
     records = []
     async for m in client.iter_messages(
          echat,
          offset_date=te if te else None,
     ):
          if ts and m.date < ts:
               break

          if ts and te:
               if ts <= m.date <= te:
                    records.append(m)

     # Use CSV as data format for data...
     data = pandas.DataFrame(
          [
               {
                    "id"        : r.id,
                    "username"  : r.username,
                    "first_name": r.first_name,
                    "last_name" : r.last_name,
                    "phone"     : r.phone,
                    "bot"       : r.bot,
               }
               for r in records
          ],
          columns=[
               "id",
               "username",
               "first_name",
               "last_name",
               "phone",
               "bot",
          ],
     )

     # ... and save on disk
     path  = ffold / f"{fname}_users_{ts.date()}_{te.date()}.csv"
     nrecs = len(data)
     data.to_csv(path, index=False)

     print(f"[INFO]: {nrecs} records selected and exported to {path}")
     if AZURE_ENABLED:
          print(f"[INFO]: uploading records to Azure Blob Storage {AZURE_STORAGE_ACCOUNT}/{AZURE_STORAGE_ACCOUNT_BLOB}...")
          bstorage = azure_integration.get_container(AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_ACCOUNT_BLOB)
          azure_integration.push_container(bstorage, path)
          print(f"[INFO]: uploaded completed!")

     # TODO: integration with AWS

     return len(data)