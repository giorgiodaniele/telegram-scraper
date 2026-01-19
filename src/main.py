import asyncio
import os
import sys
import telethon
import datetime
import dotenv
import argparse

import select_messages
import select_accounts
import delete_messages

from   pathlib import Path

dotenv.load_dotenv()

# Telegram
TELEGRAM_API_ID    = os.environ["TELEGRAM_API_ID"]
TELEGRAM_API_HASH  = os.environ["TELEGRAM_API_HASH"]

def parse_utc(value):
     if not value:
          return None
     return datetime.datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)

def ensure_output_dir() -> Path:
    folder = Path(__file__).parent / ".." / "data"
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def arguments():
     parser = argparse.ArgumentParser()

     parser.add_argument(
          "--ts",
          required=True,
          type=parse_utc,
     )

     parser.add_argument(
          "--te",
          required=True,
          type=parse_utc,
     )

     parser.add_argument(
          "--action",
          required=True,
          choices=[
               "delete-messages",
               "select-messages",
               "select-accounts"
          ],
          type=str
     )

     parser.add_argument(
          "--chat-name",
          required=True,
          type=str
     )

     return parser.parse_args()


async def main():

     ################################################################################
     #                                  MAIN                                        #
     #                                                                              #
     ################################################################################

     args = arguments()
     
     # Generate a new client
     session = "telegram_client_session"
     client  =  telethon.TelegramClient(session, api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH)

     # Start a new connection
     await client.start()

     # Select (if exists) chat by name
     chats = await client.get_dialogs()
     echat = None
     for chat in chats:
          if chat.name == args.chat_name:
               echat = chat

     if echat == None:
          sys.exit(-100)

     # Logic is here
     ffold = ensure_output_dir()
     if args.action == "delete-messages":
          await delete_messages.action(
               client=client, 
                    echat=echat, 
                    ffold=ffold, 
                    fname=args.chat_name, 
                         ts=args.ts, 
                         te=args.te)
     if args.action == "select-messages":
          await select_messages.action(
               client=client, 
                    echat=echat, 
                    ffold=ffold, 
                    fname=args.chat_name, 
                         ts=args.ts, 
                         te=args.te)
     if args.action == "select-accounts":
          await select_accounts.action(
               client=client, 
                    echat=echat, 
                    ffold=ffold, 
                    fname=args.chat_name, 
                         ts=args.ts, 
                         te=args.te)
          
     # End connection
     await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
