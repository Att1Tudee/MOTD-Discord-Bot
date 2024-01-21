import motor.motor_asyncio as motor
from environs import Env

class Dbhelper:
    def __init__(self):
        self.env = Env()
        self.env.read_env()
        self.mongodb = self.env.str('MONGODB', default='')
        self.client = motor.AsyncIOMotorClient(self.mongodb)
        self.database = self.env.str('DATABASE', default='data')
        self.db = self.client[self.database]

    async def check_channel_id(self, guild_id, channel_id):
        request_guild = str(guild_id)
        collection = self.db.get_collection(request_guild)
        existing_entry = await collection.find_one({"channel_id": channel_id})
        return existing_entry is not None
