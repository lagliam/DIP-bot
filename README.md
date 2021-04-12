# Discord Image Posting Bot (DIP-Bot)

DIP-Bot is a Discord bot takes a directory of images and posts to a channel twice a day

## Installation

### Prerequisites
Generate a new Discord bot token, only needs permission to send messages. Requires Python3

### Install
Clone this repository to your server

```git
git clone https://github.com/lagliam/DIP-bot.git
```

Place token in `.env` file

#### Command Line
 
```bash
setup.sh
```
Put your images in the `/images` folder

### Running Service

```bash
./bot.sh
```

## Usage

In the channel you want DIP-bot to post to call the following command to start posting.

```
!uWu
```

Call command again to stop posting to that channel.

## Current Issues

### Restart-ability
The bot will need users to manually restart the loop by calling the command in `Usage` twice if the server goes down, restart-ability is currently a WIP

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[GNU GPLv3 ](https://choosealicense.com/licenses/gpl-3.0/)