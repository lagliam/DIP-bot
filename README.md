# Discord Image Posting Bot (DIP-Bot)

DIP-Bot is a Discord bot takes a directory of images and posts to a channel on an interval

## Installation

### Prerequisites
Generate a new Discord bot token, only needs permission to send messages. Requires Python3

### Install
Clone this repository to your server

```git
git clone https://github.com/lagliam/DIP-bot.git
```
 Run
```bash
setup.sh
```
Put your images in the `/images` folder

Place token in `.env` file

### Running Service

```bash
docker-compose up -d
```

## Usage

### `start`
In the channel you want DIP-bot to post to call the command to start posting.

Call command again to stop posting to that channel.

### `get_one_image`
You can also get one image by calling this command

### `reset_viewed`
Delete the stored seen images file to allow previously seen images to be 
posted again

### `post_amount [1-5]`
How many images to post at a time. Has to be a number greater than 0 and 
less than 5

### `post_frequency [1-5]`
How many times per day split evenly to post. Has to be a number 
greater than 0 and less than 5

### `health_check`
Checks on the bot status by returning a message of "I'm Alive"

## Current Issues

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[GNU GPLv3 ](https://choosealicense.com/licenses/gpl-3.0/)