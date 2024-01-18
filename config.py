import motor.motor_asyncio as motor
from environs import Env

env = Env()
env.read_env()

token = env.str('TOKEN', default='')
mongodb = env.str('MONGODB')

client = motor.AsyncIOMotorClient(env_vars['MONGODB'])
db = client["data"]
collection = db["motds"]
timedb = db["time"]
