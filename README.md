# pyDisco
a lightweight Discord music bot using PyCord

## Requirements

1. Python3.9 or later
2. ffmpeg

## Installation

If you do not already have a bot token then read: 
[making your bot](#making-your-bot) for a step-by-step guide.

### **Docker (recommended)**

`docker run -i pydisco/pydisco`

Enter your bot token when prompted and you're good to go.

### Linux

TBD

### Windows

TBD

## FAQ

### Making your bot

#### Creating the token
1. Navigate to: https://discord.com/developers/applications and 'create a new application'
2. Select the application you just created and go to 'bot' press  'add bot'
3. After the bot has been created you can then click 'view token'
4. If you are not running the Dockerised version then you need to enter this token into `config.txt` manually
5. Take note of the bot's application id (viewable under 'general information') as this is required for step 2.

#### Invite the bot to your server(s)

1. Enter the following URL, replacing: [APPLICATION_ID] with the application ID generated earlier.
* `https://discord.com/api/oauth2/authorize?client_id=[APPLICATION_ID]&permissions=0&scope=bot`
2. The bot has been designed around requiring minimal Discord Oauth2 permissions so the above `&permissions=0&scope=bot` should suffice.

## Licensing

pyDisco is built on PyCord (MIT) and the LGPLv3 version of ffmpeg.
