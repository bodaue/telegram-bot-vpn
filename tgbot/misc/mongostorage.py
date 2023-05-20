from typing import Any, Dict, Optional

from aiogram import Bot
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from motor.motor_asyncio import AsyncIOMotorClient


class MongoStorage(BaseStorage):
    def __init__(self, uri: str, database: str, collection_states: str) -> None:
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[database]
        self.collection = self.db[collection_states]

    async def set_state(self, bot: Bot, key: StorageKey, state: StateType = None) -> None:
        state = state.state if isinstance(state, State) else state
        await self.collection.update_one(filter={'key': key.__dict__},
                                         update={'$set': {"state": state}},
                                         upsert=True)

    async def get_state(self, bot: Bot, key: StorageKey) -> Optional[str]:
        data = await self.collection.find_one(filter={'key': key.__dict__})
        if data:
            return data.get('state')
        return None

    async def set_data(self, bot: Bot, key: StorageKey, data: Dict[str, Any]) -> None:
        await self.collection.update_one(filter={'key': key.__dict__},
                                         update={'$set': {"data": data}},
                                         upsert=True)

    async def get_data(self, bot: Bot, key: StorageKey) -> Dict[str, Any]:
        result = await self.collection.find_one(filter={'key': key.__dict__})
        return result.get('data') if result else {}

    async def close(self) -> None:
        self.client.close()
        pass
