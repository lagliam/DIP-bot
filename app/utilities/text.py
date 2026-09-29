"""User-facing strings, kept out of the command logic."""

from __future__ import annotations

# --- posting lifecycle ---------------------------------------------------------
RESTART_POSTING = "Posting restarted"
START_POSTING = "Posting started"
START_POSTING_HELP = "Starts posting images to the channel where the start posting command was called"
START_POSTING_REPEAT = "Posting has already been started for this channel"
STOP_POSTING = "Posting stopped"
STOP_POSTING_HELP = "Stops posting images in the channel where the command is called"
STOP_POSTING_REPEAT = "Posting has not been started for this channel"
POSTING_NOT_STARTED = "Posting has not started for this channel"

# --- images --------------------------------------------------------------------
GET_IMAGE = "Here's a pic for you"
GET_IMAGE_HELP = "Returns one picture and marks it as viewed"
NO_MORE_TO_SEE = "No more images to see."
PREVIEW_HELP = "See a preview of images this bot will post"
NO_IMAGES_TO_PREVIEW = "There are no images to preview"
TOP_LIKED_HELP = "Get the top liked image posted to this channel"
NO_LIKED_IMAGES = "No one has reacted to an image in this channel yet"
LIKED_IMAGE_MISSING = "The top liked image is no longer in the library"

# --- schedule ------------------------------------------------------------------
POST_AMOUNT_HELP = "How many images to post at a time. Number between [1-5]"
POST_AMOUNT_END = "Saved number to be posted"
CHANGE_FREQUENCY_HELP = "How many times per day in even intervals to post images to the channel"
CHANGE_FREQUENCY_END = "Saved frequency of posts"
NEXT_POST_DETAILS_HELP = "How many images and how long until the next post is in minutes"
RESET_VIEWED_HELP = "Resets the list of previously viewed images back to zero"
RESET_VIEWED_MESSAGE = "Previously viewed have been added back into the mix -"
RESET_LAST_VIEWED_HELP = (
    "Resets the last time an image was sent so new images will be sent to the channel"
)
RESET_LAST_VIEWED_RESPONSE = "Last viewed time has been reset, expect new posts within the next 5 minutes"
STATS_HELP = "Stats about the bot interactions"

# --- admin ---------------------------------------------------------------------
HEALTH_CHECK_HELP = 'Responds with "I\'m Alive" if running'
HEALTH_CHECK_RESPONSE = "I'm alive!"
PERMISSIONS = "Must be server owner or have an administrator role to use command."
PRIVATE_PERMISSIONS = "You do not have permission to send private commands to the bot"
PRIVATE_CHANNEL_DENY = "Unable to process command, sent from a private channel"
DENY_PRIVATE_MESSAGES = "You cannot use this command in a private message"

# --- help ----------------------------------------------------------------------
HELP_HELP = "Displays a help message"

POPULAR_COMMANDS = (
    "`/start` - Starts posting to a channel on a daily interval\n"
    "`/stop` - Stops posting\n"
    "`/images get_one_image` - Gets an image and posts it immediately"
)

COMMAND_GROUPS = (
    "`/images` - fetch images on demand\n"
    "`/posts` - inspect and adjust the posting schedule\n"
    "`/admin` - health check"
)


def bot_description(name: str) -> str:
    """The blurb shown by ``/help``."""
    return (
        f"{name} is a versatile Discord bot designed to enhance your server's visual "
        f"experience by automatically posting images at predefined intervals. Whether "
        f"you're looking to showcase artwork, memes, or any other visual content, the "
        f"bot makes it easy to keep your server engaged with fresh and exciting images."
    )
