#!/usr/bin/env python3.6
import configobj
from pushbullet import Pushbullet
import praw
import re
from pathlib import Path


class MechMarketScrape(object):
    def __init__(self, keyword, search_regex, price_regex, praw_instance, subreddit, pb):
        """

        :type keyword: str
        :type search_regex: str
        :type price_regex: str
        :type praw_instance: praw.reddit.Reddit
        :type subreddit: str
        :type pb: Pushbullet
        """
        self.keyword = keyword
        self.search_regex = re.compile(search_regex)
        self.praw = praw_instance
        self.strip_regex = re.compile(r'https://www\.(?P<url>.*comments/[^/]*)/.*$')
        self.timestamp_regex = re.compile(r'.*\[[Tt]imestamp[^\]]*\]\((?P<imguralbum>[^)]+).*', flags=re.MULTILINE)
        self.imgur_regex = re.compile(r'.*\[[^\]]+\]\((?P<imgur_link>[^)]+)\).*')
        self.subreddit = self.praw.subreddit(subreddit)
        self.pb = pb
        price_regex = price_regex.format(self.keyword)
        self.price_regex = re.compile(price_regex)

    def start(self):
        for submission in self.subreddit.stream.submissions():
            self.filter_posts(submission)

    def find_price(self, self_text):
        """

        :type self_text: str
        """
        self_text_list = [foo.lower() for foo in self_text.splitlines()]
        for line in self_text_list:
            match = self.price_regex.match(line)
            if match:
                prefix_unit = match.group('prefix_unit')
                price = match.group('price')
                postfix_unit = match.group('postfix_unit')
                # $50
                if prefix_unit is not None:
                    return '{}{}'.format(prefix_unit, price)
                # 50 USD
                elif postfix_unit is not None:
                    return '{} {}'.format(price, postfix_unit)
                # HURR DURR
                else:
                    return '{} Schmeckles (the dingus didnae set a currency! Or the regex sucks.)'.format(price)

    def filter_posts(self, submission):
        """

        :type submission: praw.models.reddit.submission.Submission
        """
        title = submission.title
        link = submission.permalink
        if self.search_regex.match(title):
            self_text = submission.selftext
            title_match = self.search_regex.match(title)
            location = title_match.group('location')
            selling = title_match.group('selling')
            asking = title_match.group('asking')
            timestamp_album = self.find_timestamp_album(self_text)
            pb_title = 'Location: {}\nSelling: {}\nAsking: {}'.format(location, selling, asking)
            print(pb_title)
            print('Timestamp images:')
            print('Posting text:')
            print(self_text)
            price = self.find_price(self_text)
            pretty_url = 'https://www.reddit.com{}'.format(link)
            self.pb.push_link('Matched listing!', pretty_url)
            self.pb.push_note('Post title:', pb_title)
            self.pb.push_note('Price', 'Price: {}'.format(price))
            self.pb.push_link('Timestamp album', timestamp_album)

    def find_timestamp_album(self, self_text):
        """

        :type self_text: str
        """
        # Sometimes, people put multiple timestamp images in their posts. Typically, these are in-line with the item.
        # if this is the case, then we'll go through and look for any image that says "timestamp". If they're SUPER
        # awesome then even that won't match up right, so we'll just look for any imgur link in that line.
        if len(self.timestamp_regex.findall(self_text)) > 1:
            for line in [foo.lower() for foo in self_text.splitlines()]:
                if self.price_regex.match(line):
                    if self.timestamp_regex.findall(line)[0]:
                        return self.timestamp_regex.findall(line)[0]
                    else:
                        return self.imgur_regex.findall(line)[0]
            else:
                return self.timestamp_regex.findall(self_text)[0]
        else:
            return self.timestamp_regex.findall(self_text)[0]


def main():
    script_directory = Path(__file__).resolve().parents[0]
    config = script_directory / 'mm-watch.cfg'
    config_options = configobj.ConfigObj(str(config), file_error=True)
    pushbullet_access_token = config_options['pushbullet_access_token']
    pb = Pushbullet(pushbullet_access_token)
    user_agent = config_options['user_agent']
    client_id = config_options['client_id']
    client_secret = config_options['client_secret']
    username = config_options['username']
    password = config_options['password']
    subreddit = config_options['subreddit']
    keyword = config_options['keyword']
    price_regex_pattern = config_options['price_regex_pattern']
    title_regex = config_options['title_regex']
    praw_instance = praw.Reddit(user_agent=user_agent, client_id=client_id, client_secret=client_secret,
                                username=username, password=password)
    reddit_get = MechMarketScrape(keyword, title_regex, price_regex_pattern, praw_instance, subreddit, pb)
    reddit_get.start()


main()
