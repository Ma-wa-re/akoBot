import aiohttp
import configparser
import os

class LoadPlugin:

    description = 'Get osu! data for users and beatmaps'
    # When the plugin is loaded
    def __init__(self, client):
        self.client = client
        self.api_key = ''
        self.loaded_config = False
        self.load_Config()

    # Load osu Config file form config folder
    def load_Config(self):
        if os.path.isfile('config/osu.ini'):
            config = configparser.ConfigParser()
            config.read('config/osu.ini')
            self.loaded_config = True
            self.api_key = config['OSU']['Key']

    # Function to get osu! user data
    async def osu_user(self, user, mode, channel):
        # Convert mode into relevant number for osu api
        mode_number = 0
        if mode.lower() == 'osu':
            mode_number = 0
        elif mode.lower() == 'taiko':
            mode_number = 1
        elif mode.lower() == 'ctb':
            mode_number = 2
        elif mode.lower() == 'mania':
            mode_number = 3

        # Make api link
        url = 'https://osu.ppy.sh/api/get_user?k=' + self.api_key + '&u=' + user + '&m=' + str(mode_number)

        #  Request data
        data = []
        aioclient = aiohttp.ClientSession()
        async with aioclient.get(url) as resp:
            data = await resp.json()
        aioclient.close()

        try:
            msg = '''```\nLevel: {0}\nRank: {1}\nPP: {2}\nAccuracy: {3}\nCountry: {4}\nCountry Rank: {5}\nPlay Count: {6}\nRanked Score: {7}\nTotal Score: {8}\nNo of SS: {9}\nNo of S: {10}\nNo of A: {11}```'''

            # Download users osu! avatar
            avatar_url = 'https://a.ppy.sh/' + data[0]['user_id']
            aioclient = aiohttp.ClientSession()
            async with aioclient.get(avatar_url) as resp:
                avatar_data = await resp.read()
                with open("temp.png", "wb") as f:
                    f.write(avatar_data)
                    f.close()
            aioclient.close()

            # Send the osu! name and mode
            await self.client.send_message(channel,  'osu! Info for {0} ({1}):'.format(data[0]['username'], mode))
            # Send the avatar then delete for machine
            await self.client.send_file(channel, 'temp.png')
            os.remove('temp.png')
            # Send rest of osu! user info
            await self.client.send_message(channel, msg.format(data[0]['level'], data[0]['pp_rank'], data[0]['pp_raw'], data[0]['accuracy'], data[0]['country'], data[0]['pp_country_rank'], data[0]['playcount'], data[0]['ranked_score'], data[0]['total_score'], data[0]['count_rank_ss'], data[0]['count_rank_s'], data[0]['count_rank_a']))

        except IndexError:
            # If user not found (banned or typed wrong) send a message
            await self.client.send_message(channel, 'User Not Found')

    # Fuction to get osu beatmap info
    async def osu_beatmap(self, oid, oset, channel):
        url = ''
        if oset:
            # Single Beatmap
            url = 'https://osu.ppy.sh/api/get_beatmaps?k=' + self.api_key + '&b=' + str(oid)
        else:
            # Beatmap Set
            url = 'https://osu.ppy.sh/api/get_beatmaps?k=' + self.api_key + '&s=' + str(oid)

        #  Request data
        data = []
        aioclient = aiohttp.ClientSession()
        async with aioclient.get(url) as resp:
            data = await resp.json()
        aioclient.close()

        if oset:
            # Single beatmap
            try:
                msg = '```\nTitle: {0}\nArtist: {1}\nCreator: {2}\nBPM: {3}\nSource: {4}\nState: {5}\nDifficulty Name: {6}\nLength: {7}\nStars: {8}\nCS: {9}\nOD: {10}\nAR: {10}\nHP: {12}\nMax Combo: {13}\n```\nosu!direct: <osu://dl/{14}>\nBeatmap Link: https://osu.ppy.sh/s/{14}'

                #Change Ranked state to string
                state = ''
                if data[0]['approved'] == '-2':
                    state = 'Graveyard'
                elif data[0]['approved'] == '-1':
                    state = 'WIP'
                elif data[0]['approved'] == '0':
                    state = 'Pending'
                elif data[0]['approved'] == '1':
                    state = 'Ranked'
                elif data[0]['approved'] == '2':
                    state = 'Approved'
                elif data[0]['approved'] == '3':
                    state = 'Qualified'

                # Get length in mins and seconds
                mins = int(int(data[0]['total_length']) / 60)
                secs = int(data[0]['total_length']) % 60
                length = str(mins) + ' min(s) ' + str(secs) + ' seconds'

                await self.client.send_message(channel, msg.format(data[0]['title'], data[0]['artist'], data[0]['creator'], data[0]['bpm'], data[0]['source'], state, data[0]['version'], length, data[0]['difficultyrating'], data[0]['diff_size'], data[0]['diff_overall'],  data[0]['diff_approach'], data[0]['diff_drain'], data[0]['max_combo'],  str(data[0]['beatmapset_id'])))
            except IndexError:
                # If beatmap not found
                await self.client.send_message(channel, 'Beatmap Not Found')
        else:
            # Beatmap Set
            try:
                msg = 'Beatmap set\n```\nTitle: {0}\nArtist: {1}\nCreator: {2}\nBPM: {3}\nSource: {4}\nState: {5}\nLength: {6}\nNumber of difficulties: {7}\n```\nosu!direct: <osu://dl/{8}>\nBeatmap Link: https://osu.ppy.sh/s/{8}'

                # Change Ranked state to string
                state = ''
                if data[0]['approved'] == '-2':
                    state = 'Graveyard'
                elif data[0]['approved'] == '-1':
                    state = 'WIP'
                elif data[0]['approved'] == '0':
                    state = 'Pending'
                elif data[0]['approved'] == '1':
                    state = 'Ranked'
                elif data[0]['approved'] == '2':
                    state = 'Approved'
                elif data[0]['approved'] == '3':
                    state = 'Qualified'

                # Get length in mins and seconds
                mins = int(int(data[0]['total_length']) / 60)
                secs = int(data[0]['total_length']) % 60
                length = str(mins) + ' min(s) ' + str(secs) + ' seconds'

                await self.client.send_message(channel, msg.format(data[0]['title'], data[0]['artist'], data[0]['creator'], data[0]['bpm'], data[0]['source'], state, length, len(data), str(data[0]['beatmapset_id'])))
            except IndexError:
                # If beatmap not found
                await self.client.send_message(channel, 'Beatmap Not Found')

    async def run(self, message):
        # Check there is an argument for osu command
        if len(message.content) <= 4:
            return False
        else:
            if message.content[4] == ' ':
                command_full = message.content.replace(self.client.serverConfig[message.server.id]['Prefix'] + 'osu ', '')
            else:
                command_full = message.content.replace(self.client.serverConfig[message.server.id]['Prefix'] + 'osu', '')

            # osu user info
            if 'osu.ppy.sh/u/' in command_full or command_full.startswith('user'):
                user = ''
                mode = 'osu'

                # If user is given as a link
                if 'osu.ppy.sh/u/' in command_full:
                    temp = command_full.split('/u/')

                    # If user specifics the game mode
                    if 'mode=' in temp[1]:
                        user_mode_string = temp[1].replace(' ', '')
                        user_mode = user_mode_string.replace('mode=', ' ').split(' ')
                        user = user_mode[0]
                        mode = user_mode[1]
                    else:
                        user = temp[1].split(' ')[0]
                else:
                    # Else user is given by name
                    temp = command_full.replace(' ', '%20')

                    # If user specifics the game mode
                    if 'mode=' in temp:
                        user_mode_string = temp.replace('user%20', '')
                        if '%20mode=' in user_mode_string:
                            user_mode = user_mode_string.replace('%20mode=', ' ').split(' ')
                        else:
                            user_mode = user_mode_string.replace('mode=', ' ').split(' ')

                        user = user_mode[0]
                        mode = user_mode[1]
                    else:
                        user = temp.replace('user%20', '')
                # Run command and return true
                await self.osu_user(user, mode, message.channel)
                return True

            # osu beat map info
            elif  'osu.ppy.sh/b/' in command_full or 'osu.ppy.sh/s/' in command_full:
                single = True
                if 'osu.ppy.sh/b/' in command_full:
                    id = str(command_full.split('/b/')[1].split('&')[0])
                    single = True
                elif 'osu.ppy.sh/s/' in command_full:
                    id = str(command_full.split('/s/')[1])
                    single = False

                if len(id) == 0:
                    await self.client.send_message(message.channel, 'Not a valid beatmap')
                else:
                    await self.osu_beatmap(str(id), single, message.channel)

                return True

            # Help
            elif command_full == 'help':
                msg = 'osu! commands:\n```\nUser Info: <user (name/id)/profile link> mode=<mode> (mode is optional defaults to osu)\nBeatmap Info: <Beatmap set link/diff link>\n```'
                await self.client.send_message(message.channel, msg)
                return True

            # Return false if no command
            return False
