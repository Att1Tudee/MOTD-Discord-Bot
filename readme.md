Discord message of the day bot runtime.

Set up 


What you need

You need to have mongoDB database access, it's free to use
https://www.mongodb.com/cloud/atlas/register

You need to have discordbot to use, register one in 
https://discord.com/developers/applications

You need Docker installed 

create .env file with these information
TOKEN="<discord-bot-token>"
MONGODB="<mongodb-connection-string>"
DATABASE="data"

add .env file inside both discordbot and webclient folders. 

docker compose up in discordbot folder

docker compose up in webclient folder(WIP)

