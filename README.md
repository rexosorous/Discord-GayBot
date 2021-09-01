# Discord-GayBot
This is a complete rewrite of my [discord-bot](https://github.com/rexosorous/discord-bot) which was something really quick I threw together just to see and learn how discord bots worked. I never took it that seriously and kind of just added whatever fun or stupid features I wanted. As a result, the code was a mess and extremely difficult to read and understand. So much so that I started over from scratch instead of fixing what was there.

Now that I've matured at least a little bit as a developer, this will (hopefully) be a much cleaner code that strives towards my own ideals.

## Dependencies / Requirements

### Python 3.5.3+ (restricted by discord.py)

### pip packages
* [discord.py[voice]](https://github.com/Rapptz/discord.py)
* [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) and it's requirements
* [youtube-dl](https://github.com/ytdl-org/youtube-dl)

### Programs
* [ffmpeg](https://ffmpeg.org/download.html). If you're on Windows, make sure to install it to PATH

## Discord Permissions

The bot requires these discord permissions to function properly
* Send Messages
* Embed Links
* Add Reactions
* Manage Messages
* Read Message History

## Setup

* Your discord bot token must be placed in the `login.token` file
* If you wish to be able to play age-restricted videos from youtube, log into an account that's able to watch those vidoes and put your cookies in the `cookiex.txt` file
    - I'm not really sure which cookies are needed, so I just put them all in using this [google chrome extension](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid?hl=en)

## Running

Run `GayBot.py` like you would any other python script.

Something like `py GayBot.py`

## Quirks

* There is no logger (yet)
* Uses the default discord.py help command and can show some funny stuff based on how I commented everything
