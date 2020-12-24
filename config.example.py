from discord.ext import commands
import logging
import os
from datetime import datetime
uptime = datetime.now()
cache = []

token = '[TOKEN]'
description ='Lynn'
gitURI = "git@github.com:Fam0r/Lynn3.git"

dbConfig = {
    "database": "lynnDB",
    "user": "pi",
    "password": "pass123",
    "host": "raspberry.pi",
    "port": "5432"
}
useDB = True

os.makedirs('logs', exist_ok=True)
logging.basicConfig(format='%(asctime)s | [%(levelname)s] (%(filename)s) - %(message)s',
                    level=logging.INFO,
                    handlers=[
                        logging.FileHandler(f'logs/{datetime.now().strftime("%Y-%m-%d")}.log'),
                        logging.StreamHandler()
                    ])

def get_prefix(bot, message):
    prefixes = ['%', 'lynn ']
    return commands.when_mentioned_or(*prefixes)(bot, message)

apiKeys = {
    'tracker':          '[KEY]',
    'steam':            '[KEY]',
    'omdb':             '[KEY]',
    'twitterConsKey':   '[KEY]',
    'twitterConsSecret':'[KEY]',
    'twitterAccToken':  '[KEY]',
    'twitterAccSecret': '[KEY]',
    'osu':              '[KEY]',
    'twitchID':         '[KEY]',
    'twitchSecret':     '[KEY]',
    'wolframalpha':     '[KEY]',
    'ocrspace':         '[KEY]',
    'newsapi':          '[KEY]'
    #'openweathermap':   '[KEY]'
}

statusPages = [
    # Unfortunately statuspage.io doesn't include system metrics in their API.
    # System metric IDs must be hardcoded because of that.
    # TODO: BeautifulSoup scraping?
    ('discord', 'https://discordstatus.com', ('ztt4777v23lf',)),
    ('twitter', 'https://api.twitterstat.us', None),
    ('reddit', 'https://reddit.statuspage.io', ('rx2nb3pfx3w6', '0jwzw9drbt3d', '5nx0js42cvh6', 'ykb0vk6gm40h', 'k7t111j3ykjr', 'zry7jgt3xffg')),
    ('cloudflare', 'https://www.cloudflarestatus.com', None),
    ('dropbox', 'https://status.dropbox.com', None),
    ('github', 'https://www.githubstatus.com', None),
    ('medium', 'https://medium.statuspage.io', ('kb1b7qv1kfv1', 'd9gjgw59bwfz', 'lwb7fbwqljjz')),
    ('epicgames', 'https://status.epicgames.com', None),
    ('glitch', 'https://status.glitch.com', ('2hfs13clgy2x', 'lz9n5qdj9h67', '4kppgbgy1vg6', 'yfyd7k8t6c2t', 'f9m2jkbys0lt', '8hhlmmyf9fqw'))
]