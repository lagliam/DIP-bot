# text.py
# contains the text constants for the project

START_POSTING = 'Posting started'
START_POSTING_HELP = 'Starts posting images to the channel where the start posting command was called'
START_POSTING_REPEAT = 'Posting has already been started for this channel'
STOP_POSTING_HELP = 'Stops posting images in the channel where the command is called'
STOP_POSTING_REPEAT = 'Posting has not been started for this channel'
STOP_POSTING = 'Posting stopped'
GET_IMAGE = "Here's a pic for you"
GET_IMAGE_HELP = 'Returns one picture and marks it as viewed'
RESET_VIEWED_MESSAGE = 'Previously viewed have been added back into the mix -'
RESET_VIEWED_HELP = 'Resets the list of previously viewed images back to zero'
POST_AMOUNT_HELP = 'How many images to post at a time. Number between [1-5]'
POST_AMOUNT_ERROR = 'Value must be lower than 5 but greater than 0'
POST_AMOUNT_END = 'Saved number to be posted'
CHANGE_FREQUENCY_ERROR = 'Value must a number be lower than 5 but greater than 0'
CHANGE_FREQUENCY_HELP = 'How many times per day in even intervals to post images to the channel'
CHANGE_FREQUENCY_END = 'Saved frequency of posts'
NO_MORE_TO_SEE = '(o･｀Д´･o)! No more images to see'
HEALTH_CHECK_HELP = "Responds with \"I'm Alive\" if running"
HEALTH_CHECK_RESPONSE = "I'm alive!"
POSTING_NOT_STARTED = 'Posting has not started for this channel'
NEXT_POST_DETAILS_HELP = 'How many images and how long until the next post is in minutes'
STATS_HELP = 'Stats about the bot interactions'
PREVIEW_HELP = 'See a preview of images this bot will post'
TOP_LIKED_HELP = 'Get the top liked image posted to this channel'
PERMISSIONS = 'Must be guild owner or have custom permissions set to use command'
ADD_USER_HELP = 'Adds a user to be able to use bot commands at the guild'
ADD_USER_RESPONSE = 'User can now use bot commands'
REMOVE_USER_HELP = 'Removes a user to be able to use bot commands at the guild'
REMOVE_USER_RESPONSE = 'User can no longer use bot commands'
PRIVATE_CHANNEL_DENY = 'Unable to process command, sent from a private channel'
PRIVATE_PERMISSIONS = 'You do not have permission to send private commands to the bot'
RESET_LAST_VIEWED_HELP = 'Resets the last time an image was sent so that new images will be sent to the channel'
RESET_LAST_VIEWED_RESPONSE = 'Last viewed time has been reset, expect new posts within the next 5 minutes'
DENY_PRIVATE_MESSAGES = 'You cannot use this command in a private message'
