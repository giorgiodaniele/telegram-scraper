import asyncio
import argparse
import datetime as dt
import pandas   as pd
import os
import dotenv
from   pathlib            import Path
from   azure.identity     import DefaultAzureCredential
from   azure.storage.blob import BlobServiceClient

from client import Client



UTC = dt.timezone.utc


def parse_utc(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    return dt.datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


"""
Azure Blob helpers
"""

def azure_enabled() -> bool:
    return os.getenv("AZURE_ENABLED", "false").lower() == "true"


def get_container_client():
    if not azure_enabled():
        return None

    account_url = os.environ["ACCOUNT_URL"]
    container   = os.environ["CONTAINER"]

    credential = DefaultAzureCredential()
    service    = BlobServiceClient(account_url, credential=credential)

    return service.get_container_client(container)


def upload_file(storage, path: Path) -> None:

    if storage is None:
        return

    with path.open("rb") as f:
        storage.upload_blob(path.name, f, overwrite=True)


"""
Telegram helpers
"""


async def save_messages(
    client: Client,
    entity,
    folder: Path,
    storage,
    chat_name: str,
    ts,
    te,
):
    messages = await client.select_messages(entity=entity, ts=ts, te=te)

    data = pd.DataFrame(
        [
            {
                "id"    : m.id,
                "date"  : m.date,
                "text"  : m.message,
                "sender": m.from_id.user_id,
            }
            for m in messages if m.message
        ],
        columns=["id", "date", "text", "sender"],
    )

    path = folder / f"{chat_name}_messages_{ts}_{te}.csv"
    data.to_csv(path, index=False)

    upload_file(storage, path)
    print(f"[INFO] saved {len(data)} messages")


async def save_users(
    client: Client,
    entity,
    folder: Path,
    storage,
    chat_name: str,
    ts,
    te,
):
    users = await client.select_all_users(entity=entity)

    df = pd.DataFrame(
        [
            {
                "id"        : u.id,
                "username"  : u.username,
                "first_name": u.first_name,
                "last_name" : u.last_name,
                "phone"     : u.phone,
                "bot"       : u.bot,
            }
            for u in users
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

    path = folder / f"{chat_name}_users_{ts}_{te}.csv"
    df.to_csv(path, index=False)

    upload_file(storage, path)
    print(f"[INFO] saved {len(df)} users")


async def save_photos(
    client: Client,
    entity,
    folder: Path,
    storage,
    chat_name: str,
    ts,
    te,
):
    photos = await client.select_photos(
        entity=entity,
        folder=str(folder),
        ts=ts,
        te=te,
    )

    for photo_path in photos:
        upload_file(storage, Path(photo_path))

    print(f"[INFO] saved {len(photos)} photos")


async def cancel_my_messages(
    client: Client,
    entity,
    ts,
    te,
):
    found, deleted = await client.delete_my_messages(
        entity=entity,
        ts=ts,
        te=te,
    )

    print(f"[INFO] found {found}, deleted {deleted} messages")




def parse_args():
    parser = argparse.ArgumentParser()

    # The --action argument defines which operation will be executed 
    # on the selected Telegram chat.

    # Each action triggers exactly one isolated workflow:

    # - save-messages
    #     Fetches all messages in the selected chat within the optional
    #     time window (ts, te), extracts structured fields
    #     (id, date, text, sender), writes them to a CSV file,
    #     and uploads the file to Azure Blob Storage.

    # - save-users
    #     Retrieves all users participating in the selected chat,
    #     extracts public profile information, saves it to a CSV file,
    #     and uploads it to Azure Blob Storage.

    # - save-photos
    #     Downloads all photos from the selected chat within the optional
    #     time window, stores them locally, and uploads each photo
    #     to Azure Blob Storage.

    # - canc-my-messages
    #     Finds all messages sent by the authenticated user in the selected
    #     chat within the optional time window and permanently deletes them.

    # Only one action can be executed per run.


    parser.add_argument("--chat-name", required=True)
    parser.add_argument("--ts")
    parser.add_argument("--te")
    parser.add_argument(
        "--action",
        required=True,
        choices={
            "save-messages",
            "save-users",
            "save-photos",
            "canc-my-messages",
        },
    )

    return parser.parse_args()


async def main() -> None:
    dotenv.load_dotenv()

    args = parse_args()

    ts = parse_utc(args.ts)
    te = parse_utc(args.te)

    base_dir     = ensure_dir(Path("../data"))
    messages_dir = ensure_dir(base_dir / "messages")
    users_dir    = ensure_dir(base_dir / "users")
    photos_dir   = ensure_dir(base_dir / "photos")

    container = get_container_client()

    client = Client(api_id=os.environ["TELEGRAM_API_ID"], api_hash=os.environ["TELEGRAM_API_HASH"])

    await client.connect()
    try:
        entity = await client.select_dialog(args.chat_name)
        chat   = args.chat_name.replace(" ", "_")

        match args.action:
            case "save-messages":
                await save_messages(
                    client,
                    entity,
                    messages_dir,
                    container,
                    chat,
                    ts,
                    te,
                )

            case "save-users":
                await save_users(
                    client,
                    entity,
                    users_dir,
                    container,
                    chat,
                    ts,
                    te,
                )

            case "save-photos":
                await save_photos(
                    client,
                    entity,
                    photos_dir,
                    container,
                    chat,
                    ts,
                    te,
                )

            case "canc-my-messages":
                await cancel_my_messages(
                    client,
                    entity,
                    ts,
                    te,
                )
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
