'''For a given list of VKontakte public communities' URLs,
this script retrieves raw HTML data from each URL one by one,
parses it into a data structure (list of dicts), and saves it
as CSV files. It is possible also to parse HTML raw data that
has been already saved using any browser with such an option.
'''

import sys, csv, requests

from urllib.parse import quote as quote_url
from random import choice
from bs4 import BeautifulSoup

cols = ['text','id', 'parent',  'likes', 'share', 'views']


def likes_share(soup):
    '''Returns number of Likes and Shares for the current post
    '''

    try:
        ret = list(map(
            lambda x: int(x['data-count']),
            soup.find('div', class_='like_wrap').find_all('a', class_='like_btn')
        ))

        ret += [0] * (2 - len(ret))

        return ret

    except:
        return [0, 0]


def post_views(soup):
    '''Returns number of Views of the current post message
    '''

    try:
        return int(soup.find('div', class_='like_views')['title'].split()[0])

    except:
        return 0


def post_text(soup, *, type):
    '''Returns text content of the current post message divided by '\n' symbol
    '''

    more = soup.find('a', class_=f'wall_{type}_more')

    if more:
        more.replaceWith('')

    try:
        div = soup.find('div', class_ = 
            lambda c: c.endswith(f'{type}_text')
        )

        return '\n'.join(
            filter(
                lambda s: s not in ['\n', ' '],
                div.strings
            ))

    except:
        return ''


def vk_parse(html):
    '''Parses VK posts on the wall. Input: raw html data
    Returns list of dictionaries containing post information:
    message text, id, parent id, number of likes, number of shares, number of views
    '''

    soup = BeautifulSoup(html, 'html.parser')

    data = []

    id, pid, post_id = 1, 0, 0

    for post in soup.find_all('div', class_='_post_content'):
        if len(post['class']) > 1:
            type = 'reply'

            pid = post_id

        else:
            type = 'post'

            pid, post_id = 0, id

        # post message
 
        text = post_text(post, type=type)

        # post likes and views
 
        likes, share = likes_share(post)
        views = post_views(post)

        # storing data in the list

        data.append(dict(zip(
            cols,
            [text, id, pid, likes, share, views]
        )))

        id += 1

        print('Post: #' + str(id))

    return data


def vk_dump(data, fn):
    '''Writes parsed data to the csv-file with a header
    '''

    with open(fn, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames = cols,
            #delimiter = ';',
            #quoting = csv.QUOTE_MINIMAL
            quoting = csv.QUOTE_NONNUMERIC
        )

        writer.writeheader()

        for d in data:
            writer.writerow(d)


def main(fn):
    html, data = '', []

    if fn[:4] == 'http':
        fn_out = quote_url(
            fn.replace(':', '', 1).replace('//', '__').replace('/', '__'))

        h = requests.utils.default_headers()

        # random choice of the HTTP user agent
        h.update({
            'User-Agent': choice([
                'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 DuckDuckGo/7; +http://www.google.com/bot.html)',
                'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
                'Mozilla/5.0 (compatible; YandexAccessibilityBot/3.0; +http://yandex.com/bots)',
                'Mozilla/5.0 (compatible; Yahoo! Slurp/3.0; http://help.yahoo.com/help/us/ysearch/slurp)',
            ])
        })

        print('Retrieving data from url:', fn)

        req = requests.get(fn, headers=h)

        if req.status_code == requests.codes.all_ok:
            html = req.text

            with open(fn_out + '.html', 'w') as f:
                f.write(html)

        else:
            print('Error', req.status_code, 'while retrieving data from url:', fn)

    else:
        fn_out = fn

        try:
            print(f'Reading "{fn}"')
    
            with open(fn) as f:
                html = f.read()

        except FileNotFoundError:
            print('Error opening file:', fn)

    if html:
        data = vk_parse(html)

    # Writing the data into the CSV file if it has been parsed successfully
    if data:
        vk_dump(data, fn_out + '.csv')


if __name__ == '__main__' and len(sys.argv) > 1:
    for a in sys.argv[1:]:
        main(a)

else:
    print('No input file(s) specified')