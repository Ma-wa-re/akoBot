import youtube_dl
import discord
import os
import configparser

# Function to load opus libraries
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']
def load_opus_lib(opus_libs=OPUS_LIBS):  # Load Opus for voice
    if discord.opus.is_loaded():
        return True

    for opus_lib in opus_libs:
        try:
            discord.opus.load_opus('dll/' + opus_lib)
            print('Opus Loaded: ' + opus_lib)
            return
        except OSError:
            pass

class LoadPlugin:
    # Description of plugin
    description = 'Play music in a voice channel'

    def __init__(self, client):
        self.client = client
        self.use_avconv = False
        self.default_volume = 0
        self.default_length = 0
        load_opus_lib()
        self.load_Config()
        self.music_players = {}
        self.load_Musicplayers()

    # Load music Config file form config folder
    def load_Config(self):
        if os.path.isfile('config/music.ini'):
            config = configparser.ConfigParser()
            config.read('config/music.ini')
            self.use_avconv = config['MUSIC']['use_avconv']
            self.default_volume = config['MUSIC']['Volume']
            self.default_length = config['MUSIC']['Length']

    # Load music player for all servers
    def load_Musicplayers(self):
        for server in self.client.servers:
            self.music_players[server.id] = MusicPlayer(self, self.client, server)

    async def run(self, message):
        # Check is user has the manage server permission
        permissions = message.author.permissions_in(message.channel)
        admin = permissions.manage_server

        if len(message.content) <= len('music '):
            return False
        else:
            command_full = message.content.replace(self.client.serverConfig[message.server.id]['Prefix'] + 'music ', '')

            if command_full.lower() == 'connect':
                if admin:
                    await self.music_players[message.server.id].connect_voice(message)
                    await self.client.send_message(message.channel, 'Binding to this text channel and playing in **{0}**'.format(message.author.voice_channel.name))
                else:
                    await self.client.send_message(message.channel, ':warning: You need to have the manage server permission to use this command')

            elif command_full.lower() == 'disconnect':
                if admin:
                    await self.music_players[message.server.id].disconnect_voice()
                    await self.client.send_message(message.channel, 'Disconnected from **{0}**'.format(message.author.voice_channel.name))
                else:
                    await self.clientsend_message(message.channel, ':warning: You need to have the manage server permission to use this command')


# Music player
class MusicPlayer(discord.Client):

    # When loaded
    def __init__(self, plugin, client, server):
        super().__init__()
        #Bot and server it is in
        self.client = client
        self.server = server
        # Music Settings
        self.avconv = plugin.use_avconv
        self.length = plugin.default_length
        self.volume = plugin.default_volume
        # Voice client and music player
        self.player = None
        self.voice_client = None
        # Will hold dictionary with name, url and requester
        self.queue = []
        # Skip and text channel to post np
        self.skip = False
        self.max_playlist_length = 20
        self.text_channel = server.default_channel

    # Connect to voice channel
    async def connect_voice(self, message):
        # If already connected
        if self.client.is_voice_connected(self.server):
            # Move to that channel
            await self.voice_client.move_to(message.author.voice_channel)
            self.text_channel = message.channel
        else:
            # Connect to channel in that server
            self.voice_client = await self.client.join_voice_channel(message.author.voice_channel)
            self.text_channel = message.channel

    # Disconnect from voice channel
    async def disconnect_voice(self):
        # Delete Queue
        self.queue = []

        # Disconnect voice
        if self.client.is_voice_connected(self.server):
            await self.voice_client.disconnect()

        # Delete Player and voice
        self.player = None
        self.voice_client = None

    # Create player for youtube or soundcloud link to be played and start it
    async def play_link(self, url):
        # Set arguments for volume and if using avconv
        kwarg = {'use_avconv': self.avconv}
        # Make youtube_dl download song
        self.player = await self.voice_client.create_ytdl_player(url, **kwargs)
        # Play Song
        self.player.volume = self.volume
        self.player.start
