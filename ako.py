import discord
import configparser
# Import modules needed to get plugins loaded
import sys
import os
import glob

# Make Plugin folder if it does't exist
if not os.path.isdir('plugins'):
    os.makedirs('plugins')

# Load plugins folder to system path for this instance of the bot
sys.path.insert(0, os.path.realpath('plugins'))

# Load main configuration file for the bot (BotConfig.ini in the config folder)
loaded_config = False
# Look for config file
if os.path.isfile('config/BotConfig.ini'):
    # Load config if found
    config = configparser.ConfigParser()
    config.read('config/BotConfig.ini')
    loaded_config = True
else:
    # If file not found check if the config folder exists
    if not os.path.isdir('config'):
        os.makedirs('config')
    loaded_config = False

# Dictionary to store all loaded
pluginModules = {}

# Function to import all python files in the plugins folder to be used as plugins
def import_plugins():
    print('-----------------')
    print('Importing plugins')
    print('-----------------')
    # Make a list of every python file in plugins folder
    pluginsLocation = glob.glob('plugins/*.py')

    # Get plugin module name and import it and save to a dictionary
    global pluginModules
    pluginModules = {}
    if pluginsLocation:
        for plugin in pluginsLocation:
            # Get module name
            path = os.path.realpath(plugin)
            (dirname, filename) = os.path.split(path)
            (name, ext) = os.path.splitext(filename)
            # Load Module
            pluginModules[name] = __import__(name)

# First load of plugin modules before bot is started
import_plugins()

# Class for the bot will hold all information for the bot and commands that the bot can do
class ako(discord.Client):

    # Create all bot variables and load data into some
    def __init__():
        # Load info for discord.Client
        super().__init__()
        # Token so bot can login to discord
        self.token = config['MAIN']['Token']
        # Default commandPrefix for servers when the bot joins
        self.defaultPrefix = config['MAIN']['DefaultPrefix']
        # Plugins
        self.plugins = {}

    # Replace built-in run command to include our bot's token
    def start(self):
        return super().start(self.token)

    # Make each plugin an object for the bot
    def load_plugins(self):
        self.plugins = {}
        if pluginModules:
            for name, plugin in pluginModules.items():
                self.plugins[name] = plugin.LoadPlugin(self)
                print('Loaded plugin: {0}'.format(name))
