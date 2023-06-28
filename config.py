from dotenv import dotenv_values
import motor.motor_asyncio as motor

env_vars = dotenv_values('.env')

token = env_vars['TOKEN']
mongodb = env_vars['MONGODB']

client = motor.AsyncIOMotorClient(env_vars['MONGODB'])
db = client["data"]
collection = db["motds"]
timedb = db["time"]
