import json
import os

def load_server_json():
    '''
    Function to load servers.json file a make it a dictionary for bot to used.

    Arguments:
    None
    Returns:
    data - dictionary (Loaded JSON data to empty if it could to be decoded)
    '''
    data = {}
    if os.path.isfile('config/servers.json'):
        try:
            with open('config/servers.json') as data_file:
                data = json.load(data_file)
        except json.decoder.JSONDecodeError:
            data = {}

    return data

def save_server_json(data):
    '''
    Function to save data to servers.json

    Arguments:
    data - dictionary (To be encoded to JSON format)
    Returns:
    None
    '''
    with open('config/servers.json', 'w') as data_file:
        json.dump(data, data_file)

# Add server to json file
def add_server_json(data, server, settings):
    '''
    Function to add a new server to the JSON file

    Arguments:
    data - dictionary (The current setting for the servers)
    server - discord.Server (The server the to be added)
    settings - dictionary (Values of server setting to be added to server data)
    Returns:
    data - dictionary (Loaded JSON data)
    '''
    # Add values to serverConfig
    data.update({server.id: settings})
    # Save json file
    save_server_json(data)

    return data
