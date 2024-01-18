# MOTD Bot

Add message of the day from Discord client, set a time to post and you're all set.

Write !setchannel on channel you want the bot to communicate in, and !help in there for further instructions.

### Installing

You need to have docker installed. 

Bot uses MongoDB for storing messages.
You need to give bot permissions for 'manage_messages'. Anyone with 'manage_messages'-permissions can run bot commands.

You need to create a .env file in root directory which has the MongoDB address, and Discordbot token 
```sh
TOKEN = "your_discord_bot_token"
MONGODB = "your_mongodb_connection_line"
```

Once all is set,type in root directory
```sh
docker compose up -d
```

## Usage:

### Type in desired channel  
  


```sh
!setchannel
```
_sets channel where the bot posts_

```sh
!unsetchannel
```
_deletes entire channel entry from DB_

```sh
!addpost
```
_adds post in database_

```sh
!deletepost
```
_deletes post. The post needs to be exactly written as bot have saved it._

```sh
!viewpostingtime
```
_views current channel's posting time in UTC_

```sh
!viewutctime
```
_gives you current time in UTC_

```sh
!setpostingtime
```
_sets postingtime for channel in UTC. The bot posts random post at that given time._

```sh
!clear 2
```
_Clear a specified number of messages (e.g., `!clear 5`)_

```sh
!randpost
```
_posts a random post from database_

```sh
!postdatabase
```
_posts all guilds and channels saved posts with posting times_


# other commands
```sh
playing, onlinelisteningto, onlinewatching, online, idlelisteningto, idlewatching, idle, dndlisteningto, dndwatching, dnd
```
_Set bot a custom status with either word Watching or Listening to [your sentence added here]  
for example_

```sh
dndlisteningto epic music
```
_gives bot a Do Not Disturb status(red dot) with message Listening To epic music_
