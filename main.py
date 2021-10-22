"""
pyDisco
~~~~~~~~~~~~~~~~~~~
A lightweight Discord music bot in Python & Cython
:copyright: (c) 2021-present gnu-enjoyer
:license: AGPLv3, see LICENSE for more details.
"""

__title__ = 'pyDisco'
__author__ = 'gnu-enjoyer'
__license__ = 'AGPLv3'
__copyright__ = 'Copyright 2021-present gnu-enjoyer'
__version__ = '1.0.2'

import asyncio.tasks, discord, youtube_dl
from cy_utils import lst_valid, search, download, cy_init, read_config


class pyDisco(discord.Client):
    def __init__(self):
        super().__init__()
        self.prefix = '-'  # TODO: expand to config
        self.playlist = set()
        self.token = read_config()
        self.loaded = False


client = pyDisco()

commands = {
    'play', 'pause', 'skip', 'clear',
    'summon', "queue", "np", 'stop',
    'debug', 'help', 'quit', 'resume'
}

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

    @classmethod
    async def stream(cls, url):
        track = await YTDLSource.get(url)
        return cls(discord.FFmpegPCMAudio(track['url'], **ffmpeg_options), data=track)

    @classmethod
    async def get(cls, url) -> dict:
        with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
            return ydl.extract_info(url, download=False)


def get_vc(message) -> discord.VoiceClient:
    gv = discord.utils.get(
        client.voice_clients, guild=message.guild
    )

    return gv


async def playnext(message):
    gv = get_vc(message)
    lst = client.playlist[message.guild.id]

    if lst_valid(lst):
        nxt = lst.pop(0)
        found_id = search(nxt)
        player = await YTDLSource.stream(found_id[0])
        current_track(message, found_id[0])
        gv.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(playnext(message), client.loop))
        await message.channel.send(':play_pause: up next: ' + nxt)
    else:
        await message.channel.send(':stop_button: no more items in queue')
        await gv.disconnect()


async def cmd_debug(message):
    pass


async def cmd_help(message):
    info = 'commands available: ' + str(commands)
    await message.channel.send(info)


async def cmd_play(message):
    gv = get_vc(message)

    if not gv:
        await cmd_summon(message)
        gv = get_vc(message)

    playing, paused = gv.is_playing(), gv.is_paused()
    lst = client.playlist[message.guild.id]
    track = message.content[6:]

    if len(message.content) <= 6:
        if paused:
            gv.resume()
            await message.channel.send(':play_pause: resuming')
            return
        if playing:
            await message.channel.send(':no_entry_sign: already playing https://youtu.be/' + gv.trackname)
            return
        else:
            await message.channel.send(':no_entry_sign: no track entered')
            return

    if playing:
        if lst_valid(lst):
            lst.append(track)
        else:
            client.playlist[message.guild.id] = [track]

        await message.channel.send(track + ' added to queue')
        return

    found_id = search(track)

    if not found_id:
        await message.channel.send('no track found')
        return

    player = await YTDLSource.stream(found_id[0])
    current_track(message, found_id[0])
    gv.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(playnext(message), client.loop))

    await message.channel.send('playing ' + track)


async def cmd_pause(message, *argv):
    gv = get_vc(message)
    m = 'skip' if argv else 'pause'

    if gv:
        if gv.is_playing() or gv.is_paused():
            m = 'pausing' if m[0] != 's' else 'skipping'
            gv.pause()
            await message.channel.send(':fast_forward: ' + m + ' current song')
            return

    await message.channel.send(':fast_forward: nothing to ' + m)


async def cmd_skip(message, *argv):
    gv = get_vc(message)

    if not argv:
        await cmd_pause(message, True)
        current_track(message, 'nothing.')
        gv.stop()
        return
    gv.resume()
    current_track(message, gv.trackname[:-6])


async def cmd_resume(message):
    await cmd_skip(message, True)


async def cmd_clear(message, *argv):
    if lst_valid(client.playlist[message.guild.id]):
        client.playlist[message.guild.id].clear()

        if not argv:
            await message.channel.send(':new_moon_with_face: queue has been cleared.')


async def cmd_summon(message):
    if get_vc(message):
        return

    vc = message.author.voice
    await vc.channel.connect()


async def cmd_np(message):
    gv = get_vc(message)

    if not gv:
        await message.channel.send(':no_entry_sign: i am not in your voice channel')
        return

    playing, paused = gv.is_playing(), gv.is_paused()

    if playing or paused:
        l_msg = discord.Embed(
            title='now playing:',
            description='https://youtu.be/' + gv.trackname,
            colour=discord.Colour.blue()
        )
        await message.channel.send(embed=l_msg)
    else:
        await message.channel.send(':no_entry_sign: no currently played track')


async def cmd_queue(message):
    lst = client.playlist[message.guild.id]

    if not lst_valid(lst):
        lst = 'nothing!'
    else:
        lst = '\n'.join(lst)

    l_msg = discord.Embed(
        title='playlist:',
        description=lst,
        colour=discord.Colour.blue()
    )
    await message.channel.send(embed=l_msg)


async def cmd_quit(message):
    await cmd_stop(message, True)


async def cmd_stop(message, *argv):
    gv = get_vc(message)
    if not gv:
        return

    await cmd_clear(message, True)
    gv.stop()
    current_track(message, 'nothing.')

    argv = 'stopping music' if not argv else 'quitting'
    await message.channel.send(':stop_button: ' + argv + ', clearing queue')

    # TODO: Identify exact functionality;
    # some players stop+clear queue whereas others merely pause w/o resume


def current_track(message, name):
    vc = discord.utils.get(client.voice_clients, guild=message.guild)
    # Hacky
    setattr(vc, 'trackname', name)


@client.event
async def on_guild_join(guild):
    client.playlist[guild.id] = []
    print('Joined: ' + guild.name)


@client.event
async def on_guild_remove(guild):
    client.playlist[guild.id] = []
    del client.playlist[guild.id]
    print('Left: ' + guild.name)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    client.loaded = cy_init(client)


@client.event
async def on_message(message):
    if not client.loaded:
        return

    if message.author == client.user:
        return

    if not message.content.startswith(client.prefix):
        return

    if message.content.split()[0][1:].casefold() in commands:
        if not message.author.voice:
            return
        run = str(message.content.split()[0].casefold())
        await globals()['cmd_' + run[1:]](message)
        return


client.run(client.token)
