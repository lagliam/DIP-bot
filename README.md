# Discord Image Posting Bot (DIP-Bot)

DIP-Bot takes a directory of images and posts them to Discord channels on a schedule.
Each channel gets its own posting loop, tracks which images it has already seen, and
counts reactions so you can pull up the most-liked post.

## Features

- Scheduled posting per channel, 1–5 images per post, 1–5 posts per day
- Per-guild "seen image" tracking so nothing repeats until you reset it
- Reaction tracking (most-liked image lookup)
- Image reporting with automatic quarantine after 5 reports
- Oversized JPEGs are auto-compressed under Discord's 8 MB attachment limit
- Per-guild command authorization on top of the bot owner

## Requirements

- Python 3.14+
- MySQL 8 (supplied by the Docker stack, or bring your own)
- A Discord bot token with the **Send Messages** and **Read Message History**
  permissions, and the **Message Content** intent disabled (not needed)

## Installation

Clone the repository onto your server:

```bash
git clone https://github.com/lagliam/DIP-bot.git
cd DIP-bot
```

Run the setup script. It copies the example config files into place and creates the
`images/`, `db/`, `log/` and `reported_images/` directories:

```bash
./setup.sh
```

Then:

1. Put your images in `images/` (`.jpg`, `.jpeg`, `.png`, `.gif`).
2. Fill in `.env` (see below).
3. Fill in the database variables in `.env`.

### Configuration

`.env` holds every runtime secret:

| Variable | Description |
| --- | --- |
| `DISCORD_TOKEN` | Bot token from the Discord developer portal |
| `DB_HOST` | MySQL host (`db` inside Docker Compose; `localhost` for a native bot) |
| `DB_USER` | MySQL user the bot connects as |
| `DB_PASS` | Password for `DB_USER` |
| `DB_ROOT_PASS` | MySQL root password, used only to initialise the container |
| `DIPBOT_UID` / `DIPBOT_GID` | Host user/group IDs for writable Docker bind mounts; use `id -u` and `id -g` (normally both `1000`) |

`app/utilities/constants.py` holds the non-secret tunables:

| Constant | Default | Meaning |
| --- | --- | --- |
| `LIMIT_SIZE` | `8000000` | Max attachment size in bytes before compression is attempted |
| `TRIGGER_DURATION` | `86400` | Length of the scheduling window in seconds (one day) |
| `POLL_INTERVAL` | `300` | How often each channel loop re-checks whether it is due to post |
| `IMAGES_PATH` | `images/` | Directory the bot reads images from |

## Running

### Docker Compose

Brings up MySQL and the bot together:

```bash
docker compose up -d
```

Apply the database migrations (required on first run and after every upgrade):

```bash
docker exec -it bot alembic upgrade head
```

### systemd

Two units are provided in `deploy/`. Pick **one**.

**Option A — run the bot natively** (`deploy/dip-bot.service`). You supply the
database yourself. The unit assumes the repository lives at `/opt/dip-bot`, runs as a
`dipbot` user, and uses a virtualenv at `/opt/dip-bot/.venv`:

```bash
sudo useradd --system --home /opt/dip-bot --shell /usr/sbin/nologin dipbot
sudo git clone https://github.com/lagliam/DIP-bot.git /opt/dip-bot
cd /opt/dip-bot && sudo -u dipbot ./setup.sh

sudo -u dipbot python3 -m venv /opt/dip-bot/.venv
sudo -u dipbot /opt/dip-bot/.venv/bin/pip install .
sudo chown -R dipbot:dipbot /opt/dip-bot

# fill in /opt/dip-bot/.env and /opt/dip-bot/alembic.ini first
sudo -u dipbot /opt/dip-bot/.venv/bin/alembic upgrade head

sudo cp deploy/dip-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now dip-bot
```

**Option B — let systemd manage the Compose stack**
(`deploy/dip-bot-docker.service`). Same layout, but Docker runs both the bot and the
database:

```bash
sudo cp deploy/dip-bot-docker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now dip-bot-docker
```

If your repository is not at `/opt/dip-bot`, edit `WorkingDirectory`,
`EnvironmentFile`, `ExecStart` and `ReadWritePaths` in the unit before installing it.
`WorkingDirectory` must be the repository root — the bot resolves `.env`, `app/cogs`,
`images/` and `log/` relative to it.

Check status and follow logs:

```bash
systemctl status dip-bot
journalctl -u dip-bot -f
```

## Usage

Commands are grouped under `/admin`, `/images` and `/posts`, plus three top-level
commands. All responses are ephemeral unless they contain an image.

### Top level

| Command | Description |
| --- | --- |
| `/start <amount> <frequency>` | Start posting in the current channel. `amount` = images per post (1–5), `frequency` = posts per day (1–5) |
| `/stop` | Stop posting in the current channel |
| `/help` | Show bot info and the most-used commands |

### `/images`

| Command | Description |
| --- | --- |
| `/images get_one_image` | Post a single unseen image immediately |
| `/images preview` | Show a preview of images the bot will post |
| `/images get_top_liked` | Post the most-reacted-to image for this channel |

### `/posts`

| Command | Description |
| --- | --- |
| `/posts next_post_details` | How many images are queued and how many minutes until the next post |
| `/posts posting_amount <amount>` | Change images per post (1–5) |
| `/posts change_frequency <amount>` | Change posts per day (1–5) |
| `/posts reset_last_viewed` | Reset the posting timer so a new post lands within `POLL_INTERVAL` |
| `/posts reset_viewed` | Put every previously-posted image back into rotation |
| `/posts stats` | Total images sent and which channels are being posted to |

### `/admin`

| Command | Description |
| --- | --- |
| `/admin health_check` | Confirm the bot is alive |
| `/admin add_user <user>` | Authorize a user to run bot commands in this guild |
| `/admin remove_user <user>` | Revoke a user's authorization |
| `/admin report <message_id>` | Report a bot-posted image. After 5 reports the image is saved to `reported_images/` for review. Rate limited to once per 15s per user |

### Permissions

A command runs if the caller is the bot owner, the guild owner, or has been granted
access with `/admin add_user`. In DMs the caller needs the `private` permission level,
which is currently only settable directly in the `users` table.

### Reactions

Any reaction added to an image the bot posted increments that image's like counter for
the channel; removing the reaction decrements it. `/images get_top_liked` reads from
this counter.

## Database

The schema is managed exclusively by Alembic. `alembic upgrade head` works against an
empty database and is required before the bot is started for the first time.

| Table | Purpose |
| --- | --- |
| `guilds` | One row per channel being posted to: posting amount, frequency, last post time, soft-delete flag |
| `images` | One row per image sent to a guild, used to avoid repeats |
| `liked_images` | Reaction counter per (filename, guild, channel) |
| `reported_images` | Report counter per (filename, guild, channel) |
| `users` | Per-guild command authorization |
| `bot_permissions` | Lookup table: `1` none, `2` guilds, `3` private |

Run migrations after pulling a new version:

```bash
# Docker
docker exec -it bot alembic upgrade head

# native
/opt/dip-bot/.venv/bin/alembic upgrade head
```

## Project layout

```
bot.py                   entrypoint: loads cogs, registers reaction listeners
app/app.py               resumes a posting loop for every active channel on startup
app/bot/main_loop.py     per-channel scheduling loop
app/bot/image_sender.py  picks an unseen image and sends it
app/cogs/                slash command definitions
app/commands/            command logic that is too large for a cog
app/utilities/           database access, file helpers, logging, user-facing strings
alembic/versions/        database migrations
database/init.sql        initial schema for the MySQL container
deploy/                  systemd units
```

## Troubleshooting

**The bot connects but never posts.** Check that `images/` is non-empty and that the
channel has not been soft-deleted — `/posts next_post_details` reports
`Posting has not started for this channel` when it has. Re-run `/start`.

**"No more images to see".** Every image has been sent to that guild. Add more images
or run `/posts reset_viewed`.

**A large PNG is skipped.** PNGs cannot be re-compressed by the bot; only JPEGs are.
Resize the file manually or remove it.

## License
[GNU GPLv3 ](https://choosealicense.com/licenses/gpl-3.0/)