import asyncio
import datetime
import dotenv
import sys
import os
import argparse
import pandas
from   client import Client

def parse_utc(s: str) -> datetime.datetime:
    dt = datetime.strptime(s, "%Y-%m-%d")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    else:
        dt = dt.astimezone(datetime.timezone.utc)
    return dt

async def main():
    dotenv.load_dotenv()

    api_id   = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")

    # Generate a new parser
    parser = argparse.ArgumentParser()

    # Add new arguments
    parser.add_argument("--chat-name", help="Define chat name", required=True)
    parser.add_argument("--ts",        help="Define start of period (required in case of time selection)")
    parser.add_argument("--te",        help="Define end of period (required in case of time selection)")
    parser.add_argument("--action",    help="Define action to perform", 
                        choices=[
                            "save-messages",
                            "canc-messages",
                            "save-users",
                            "save-photos"
                        ], required=True)
    
    main_data_path = os.path.join("..", "data")
    if not os.path.exists(main_data_path):
        os.makedirs(main_data_path)

    photo_data_path = os.path.join("..", "data", "photos")
    if not os.path.exists(photo_data_path):
        os.makedirs(photo_data_path)

    # Get arguments from command line
    args = parser.parse_args()

    # Have a new client
    client = Client(api_id=api_id, api_hash=api_hash)
    await client.connect()

    # Fetch the entity associated with chat name
    entity = next(d.entity for d in await client.select_all_dialogs() if d.name == args.chat_name)
    if entity is None:
        sys.exit(1)

    if args.action == "save-messages":
        messages = await client.select_messages(
            entity=entity,  
            ts=parse_utc(args.ts) if args.ts else None, 
            te=parse_utc(args.te) if args.te else None,
            )
            
        file_name = f"{args.chat_name.replace(' ', '_')}_messages.csv"
        file_path = os.path.join(main_data_path, file_name)

        records  = []
        columns  = ["id", "date", "text", "sender"]
        for m in messages:
                id        = m.id
                date      = m.date
                text      = m.message
                sender    = m.from_id.user_id
                if text and len(text) > 0:
                    records.append([id, date, text, sender])
        pandas.DataFrame(records, columns=columns).to_csv(file_path, index=False)
        print(f"[INFO]: saved {len(messages)} messages in {file_path}")

    elif args.action == "canc-messages":
        found, deleted = await client.delete_my_messages(
            entity=entity,  
            ts=parse_utc(args.ts) if args.ts else None, 
            te=parse_utc(args.te) if args.te else None,
            )
        print(f"[INFO]: found {found}, deleted {deleted} messages")

    elif args.action == "save-users":
        users = await client.select_all_users(entity=entity)

        file_name = f"{args.chat_name.replace(' ', '_')}_users.csv"
        file_path = os.path.join(main_data_path, file_name)

        pandas.DataFrame([{
            "id"         : user.id,
            "username"   : user.username,
            "first_name" : user.first_name,
            "last_name"  : user.last_name,
            "phone"      : user.phone,
            "bot"        : user.bot,
        } for user in users]).to_csv(file_path, index=False)
        print(f"[INFO]: saved {len(users)} users in {file_path}")

    elif args.action == "save-photos":
        folder = os.path.join("..", "data", "photos")
        photos = await client.select_photos(
            entity=entity,
            folder= folder,
            ts=parse_utc(args.ts) if args.ts else None, 
            te=parse_utc(args.te) if args.te else None,
            )
        print(f"[INFO]: saved {len(photos)} users in {folder}")

    await client.disconnect()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()