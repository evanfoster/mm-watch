# Mech Market Watcher
I got really sick of ErgoDox keyboards getting sniped before I ever got the chance to see them. To combat this, I made a thing that will monitor the MM subreddit and alert me via Pushbullet if anything matches a particular regex.
### Installation
This only works on Python 3, and I'll probably make it Python 3.6+ soon.

Maybe I'll get around to putting this on PyPI. In the meantime, here's the dependencies:
```bash
pip install pushbullet.py praw configobj
```

### Usage
Once you've installed all of your dependencies, you should `cp mm_watch.example.cfg mm_watch.cfg`  
From that point, you'll need to fill out the conf file with your own information. The file is pretty well documented, but if you're having a hard time with it let me know and I can update it to be more clear.

Once you have your conf file good to go, simply `python mm_watch.py` and become the sniper.

Also, *please* don't commit your configuration file up. I've added it to `.gitignore` to help prevent that, but you're gonna have a realllly bad time if you're not careful.
