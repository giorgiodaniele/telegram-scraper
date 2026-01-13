import asyncio
import os
from   telethon import TelegramClient

class Client:
    def __init__(self, api_id: int, api_hash: str, session: str = "telegram_client_session"):
        self.client = TelegramClient(session, api_id, api_hash)

    async def connect(self):
        await self.client.start()
        
    async def disconnect(self):
        await self.client.disconnect()
        
    async def me(self) -> str:
        me = await self.client.get_me()
        return me.username

    async def select_all_dialogs(self):
        dialogs = await self.client.get_dialogs()
        return dialogs

    async def select_all_users(self, entity):
        users = await self.client.get_participants(entity)
        return users

    async def delete_my_messages(
        self,
        entity,
        ts,
        te,
        batch_size = 100,
    ):
        found   = 0
        deleted = 0
        batch   = []

        """
        Selects all messages sent by the logged-in user
        within a given entity (chat) and deletes them.
        """

        async for msg in self.client.iter_messages(
            entity, 
            from_user="me", 
            offset_date=te if te else None
        ):
            if ts and msg.date < ts:
                break

            found += 1
            batch.append(msg.id)

            if len(batch) == batch_size:
                try:
                    await self.client.delete_messages(entity, batch)
                    deleted += len(batch)
                except Exception:
                    pass
                batch = []
                await asyncio.sleep(0.7)

        if batch:
            try:
                await self.client.delete_messages(entity, batch)
                deleted += len(batch)
            except Exception:
                pass

        return found, deleted

    async def select_messages(
        self,
        entity,
        ts,
        te,
    ):

        records = []
        
        """
        Select all messages within entity (a chat) 
        enforcing time selection if ts and te are
        defined by caller
        """

        async for m in self.client.iter_messages(
            entity,
            offset_date=te if te else None,
        ):
            if ts and m.date < ts:
                break

            if ts and te:
                if ts <= m.date <= te:
                    records.append(m)
            else:
                records.append(m)
        return records
    

    async def select_photos(
        self,
        entity,
        folder,
        ts,
        te,
    ):


        """
        Select all messages containing a photo
        enforcing time selection if ts and te are
        defined by caller
        """

        os.makedirs(folder, exist_ok=True)
        downloaded = []

        async for m in self.client.iter_messages(
            entity,
            offset_date=te if te else None,
        ):
            if ts and m.date < ts:
                break

            if not m.photo:
                continue

            if ts and te and not (ts <= m.date <= te):
                continue

            path = await m.download_media(file=folder)
            downloaded.append(path)

        return downloaded
