import requests
import random
import re
import threading
import constants as cn
from bs4 import BeautifulSoup
from time import sleep


class Worker(threading.Thread):
    THREAD_ID = 0
    PROCESSED_OBJECTS = 0

    def __init__(self, action_queue, db_actions, mask):
        super(Worker, self).__init__()
        self.action_queue = action_queue
        self.db_actions = db_actions
        self.mask = mask
        Worker.THREAD_ID += 1
        self.id = Worker.THREAD_ID
        self.setDaemon(True)
        pass

    def run(self):

        print('>[{tid}] is live.'.format(tid=self.id))
        action_data = self.action_queue.get_next()

        while True:

            sleep(random.uniform(cn.W_THREAD_SLEEP_BEGIN_SEC, cn.W_THREAD_SLEEP_END_SEC))

            if action_data is None:
                print("> [{id}] found NO JOB.".format(id=self.id))
                sleep(cn.W_THREAD_NO_JOB_WAIT_SEC)
                action_data = self.action_queue.get_next()
                continue

            url = action_data['url']
            action = action_data['action']

            try:

                print('> [{id}] requests ({url}) with ({ip})'.format(id=self.id, url=url, ip=self.mask['ip']))
                r = requests.get(url=url, headers=self.mask['user-agent'], cookies={}, timeout=cn.REQ_TIMEOUT_SEC,
                                 proxies=self.mask['proxy'])

                # success
                if r.status_code == 200:

                    if action == cn.TYPE_LISTING:
                        self._process_listing(url, r)
                    if action == cn.TYPE_MASTER_PAGE:
                        self._process_master_page(r)
                    if action == cn.TYPE_RELEASE_PAGE:
                        self._process_release_page(r)

                    action_data = self.action_queue.get_next()

                # too many requests
                elif r.status_code == 429:
                    print('> [{id}] Error 429 - slow down - sleeping 7s.'.format(id=self.id))
                    sleep(cn.W_RESPONSE429_WAIT_SEC)
                # page not found
                elif r.status_code == 404:
                    print('> [{id}] Error 404 - remove action - could not process ({url})'.format(id=self.id, url=url))
                    action_data = self.action_queue.get_next()
                else:
                    pass

            except Exception as e:
                print('> [{id}] - Random fail [{ex}].'.format(id=self.id, ex=str(e)))
                action_data = self.action_queue.get_next()
                sleep(cn.W_RANDOM_EXCEPTION_WAIT_SEC)

            continue

    def _process_listing(self, url, r):
        print('> [{id}] - processing listing: {url}.'.format(id=self.id, url=url))
        soup = BeautifulSoup(r.text, 'lxml')

        link = soup.select_one('.pagination_next')
        if link is not None:
            master_list_url = cn.BASE_URL + link['href']
            self.action_queue.put({'url': master_list_url, 'action': cn.TYPE_LISTING})

        urls = [cn.BASE_URL + url['href'] for url in soup.select('.cards > .card > h4 > a')]
        for url in urls:
            if "/master/" in url:
                self.action_queue.put({'url': url, 'action': cn.TYPE_MASTER_PAGE})
            elif "/release/" in url:
                self.action_queue.put({'url': url, 'action': cn.TYPE_RELEASE_PAGE})

    def _process_master_page(self, r):
        soup = BeautifulSoup(r.text, 'lxml')
        id_master = r.url.split('/')[-1]
        master_name = soup.title.text.split('-')[1].strip().split(' at ')[0]
        master_year = soup.select_one('.profile a[href*=year]')
        master_year = master_year.text if master_year is not None else None
        master_rating = soup.select_one('.rating_value')
        master_rating = master_rating.text if master_rating is not None and master_rating.text != '--' else None

        artist_link = soup.select_one('#profile_title > span > span > a')
        id_artist = artist_link['href'].split('/')[2].split('-')[0]
        if not id_artist.isdigit():
            id_artist = 0
        artist_name = re.sub(r'(\"|\')', '', artist_link.text) if artist_link is not None else None

        composition_ids = [title_span['href'].split('/')[2] for title_span in
                           soup.select('td[class*="tracklist_track_title"] > a')]
        composition_titles = [title_span.text for title_span in soup.select('span[class*="tracklist_track_title"]')]
        compositions_lengths_spans = [length_span for length_span in
                                      soup.select('td[class*="tracklist_track_duration"] > span')]
        compositions_length = []

        for composition_length in compositions_lengths_spans:
            length = composition_length.text
            compositions_length.append(
                int(length.split(':')[0]) * 60 + int(length.split(':')[1]) if length is not '' else None)

        master_data = (id_master, id_artist, master_name, master_year, master_rating)
        artist_data = (id_artist, artist_name)
        genre_data = [re.sub(r'(\"|\')', '', genre.text) for genre in soup.select('.profile a[href^="/genre/"]')]
        genre_sql_data = ','.join(["('" + genre + "')" for genre in genre_data])
        style_data = [re.sub(r'(\"|\')', '', style.text) for style in soup.select('.profile a[href^="/style/"]')]
        style_sql_data = ','.join(["('" + style + "')" for style in style_data])
        composition_data = list(
            map(lambda x, y, z: (x, id_artist, y, z), composition_ids, composition_titles, compositions_length))

        master_composition_data = list(map(lambda x: (id_master, x), composition_ids))
        master_genre_data = list(map(lambda x: (id_master, x), genre_data))
        master_style_data = list(map(lambda x: (id_master, x), style_data))

        release_links = soup.select('table > tr[class*="release"] > td[class="title"] > a')
        master_release_data = [(id_master, release_link['href'].split('/')[-1]) for release_link in release_links]

        if str(artist_data).strip('[]') is not '':
            self.db_actions.put({'db_table': 'artist', 'db_values': str(artist_data).strip('[]')})
        self.db_actions.put({'db_table': 'artist', 'db_values': str(artist_data)})
        self.db_actions.put({'db_table': 'master', 'db_values': str(master_data)})
        self.db_actions.put({'db_table': 'genre', 'db_values': genre_sql_data})
        if style_sql_data is not '':
            self.db_actions.put({'db_table': 'style', 'db_values': style_sql_data})
        if str(composition_data).strip('[]') is not '':
            self.db_actions.put({'db_table': 'composition', 'db_values': str(composition_data).strip('[]')})
        self.db_actions.put({'db_table': 'master_composition', 'db_values': str(master_composition_data).strip('[]')})
        if str(master_genre_data).strip('[]') is not '':
            self.db_actions.put({'db_table': 'master_genre', 'db_values': str(master_genre_data).strip('[]')})
        if str(master_style_data).strip('[]') is not '':
            self.db_actions.put({'db_table': 'master_style', 'db_values': str(master_style_data).strip('[]')})
        self.db_actions.put({'db_table': 'master_release', 'db_values': str(master_release_data).strip('[]')})

        Worker.PROCESSED_OBJECTS += 1
        print('====================>>>>> PROCESSED: ' + str(Worker.PROCESSED_OBJECTS) + " - MASTER <<<<<=====")

    def _process_release_page(self, r):
        soup = BeautifulSoup(r.text, 'lxml')
        id_release = r.url.split('/')[-1]

        artist_link = soup.select_one('#profile_title > span > spanitemprop > a')
        id_artist = artist_link['href'].split('/')[2].split('-')[0]
        if id_artist is None or not id_artist.isdigit():
            id_artist = 0
        artist_name = re.sub(r'(\"|\')', '', artist_link.text) if artist_link is not None else None

        release_artist_data = (id_artist, artist_name)
        release_name = re.sub(r'(\"|\')', '', soup.title.text.split(' - ')[1].split(' at ')[0])

        release_year_a = soup.select_one('a[href*="year="]')
        if release_year_a is not None:
            release_year = re.findall(r'.*([1-3][0-9]{3})', release_year_a.text)[0]
        else:
            release_year = None

        release_rating = soup.select_one('span[class="rating_value"]')
        release_rating = release_rating.text if release_rating is not None and release_rating.text != '--' else None
        release_data = (id_release, id_artist, release_name, release_year, release_rating)

        composition_link = soup.select('td[class*="tracklist_track_title"] > a')
        composition_ids = [title_span['href'].split('/')[2] for title_span in composition_link]
        composition_titles = [re.sub(r'(\"|\')', '', title_span.text) for title_span in
                              soup.select('span[class*="tracklist_track_title"]')]

        compositions_lengths_spans = [length_span for length_span in
                                      soup.select('td[class*="tracklist_track_duration"] > span')]
        compositions_length = []

        for composition_length in compositions_lengths_spans:
            length = composition_length.text
            compositions_length.append(
                int(length.split(':')[0]) * 60 + int(length.split(':')[1]) if length is not '' else None)

        composition_data = list(
            map(lambda x, y, z: (x, id_artist, y, z), composition_ids, composition_titles, compositions_length))
        genre_data = [re.sub(r'(\"|\')', '', genre.text) for genre in soup.select('.profile a[href^="/genre/"]')]
        genre_sql_data = ','.join(["('" + genre + "')" for genre in genre_data])
        style_data = [re.sub(r'(\"|\')', '', style.text) for style in soup.select('.profile a[href^="/style/"]')]
        style_sql_data = ','.join(["('" + style + "')" for style in style_data])
        role_data = [role.text.split(' [')[0] for role in soup.select('.role')]
        role_sql_data = ','.join(["('" + role + "')" for role in role_data])

        artist_data = []
        credit_data = []
        credit_artists = soup.select('#credits > div[class^="section_content"] > ul > li')
        for credit_artist in credit_artists:
            role_name = re.sub(r'(\"|\')', '', credit_artist.select_one('span').text.split(' [')[0])
            artists = [(a['href'].split('/')[2].split('-')[0], a.text) for a in credit_artist.select('a')]
            artist_data += artists
            temp_credit_data = [(a['href'].split('/')[2].split('-')[0], id_release, role_name) for a in
                                credit_artist.select('a')]
            credit_data += temp_credit_data

        release_composition_data = [(id_release, composition_id) for composition_id in composition_ids]
        release_genre_data = [(id_release, genre) for genre in genre_data]
        release_style_data = [(id_release, style) for style in style_data]

        self.db_actions.put({'db_table': 'artist', 'db_values': str(release_artist_data)})
        if str(artist_data).strip('[]') is not '':
            self.db_actions.put({'db_table': 'artist', 'db_values': str(artist_data).strip('[]')})
        self.db_actions.put({'db_table': 'release', 'db_values': str(release_data)})
        self.db_actions.put({'db_table': 'composition', 'db_values': str(composition_data).strip('[]')})
        if genre_sql_data is not '':
            self.db_actions.put({'db_table': 'genre', 'db_values': genre_sql_data})
        if style_sql_data is not '':
            self.db_actions.put({'db_table': 'style', 'db_values': style_sql_data})
        if role_sql_data is not '':
            self.db_actions.put({'db_table': 'role', 'db_values': role_sql_data})
        if str(credit_data).strip('[]') is not '':
            self.db_actions.put({'db_table': 'credit', 'db_values': str(credit_data).strip('[]')})
        if str(release_genre_data).strip('[]') is not '':
            self.db_actions.put({'db_table': 'release_genre', 'db_values': str(release_genre_data).strip('[]')})
        if str(release_style_data).strip('[]') is not '':
            self.db_actions.put({'db_table': 'release_style', 'db_values': str(release_style_data).strip('[]')})
        self.db_actions.put({'db_table': 'release_composition', 'db_values': str(release_composition_data).strip('[]')})

        Worker.PROCESSED_OBJECTS += 1
        print('====================>>>>> PROCESSED: ' + str(Worker.PROCESSED_OBJECTS) + " - RELEASE <<<<<=====")
