BASE_URL = 'https://www.discogs.com'

#
# Action Descriptors
#

TYPE_LISTING = 1
TYPE_MASTER_PAGE = 2
TYPE_RELEASE_PAGE = 3
TYPE_MASTER_INSERT = 4
TYPE_RELEASE_INSERT = 5

#
# Runtime Setup
#

CRAWL_START_URL = 'https://www.discogs.com/search/?format=&track=&barcode=&genre=&anv=&catno=&year=1890-2008&contributor=&advanced=1&style=&matrix=&title=&country=serbia&artist=&label=&credit=&submitter=&type=all&page=1'
PROXY_THREADS_COUNT = 6
DB_THREADS_COUNT = 4

#
# Threading
#

DB_THREAD_NO_JOB_WAIT_SEC = 3
W_THREAD_NO_JOB_WAIT_SEC = 1
W_THREAD_SLEEP_BEGIN_SEC = 0.5
W_THREAD_SLEEP_END_SEC = 0.8
W_RESPONSE429_WAIT_SEC = 8
W_RANDOM_EXCEPTION_WAIT_SEC = 7
REQ_TIMEOUT_SEC = 7

#
# Database
#

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = 'root'
DB_DATABASE = 'discogs'

SQL_INSERT_TEMPLATE = "INSERT INTO  discogs.{db_table}({db_cols}) VALUES {db_values} ON DUPLICATE KEY UPDATE {db_pk} = {db_pk}"
SQL_INSERT_DESC = {
    'master': '`id_master`, `id_artist`, `name`, `year`, `rating`',
    'release': '`id_release`, `id_artist`, `name`, `year`, `rating`',
    'composition': '`id_composition`, `id_artist`, `name`, `length`',
    'artist': '`id_artist`, `name`',
    'genre': '`name`',
    'style': '`name`',
    'role': '`name`',
    'master_release': '`id_master`, `id_release`',
    'master_genre': '`id_master`, `genre_name`',
    'master_style': '`id_master`, `style_name`',
    'master_composition': '`id_master`, `id_composition`',
    'release_genre': '`id_release`, `genre_name`',
    'release_style': '`id_release`, `style_name`',
    'release_composition': '`id_release`, `id_composition`',
    'credit': '`id_artist`, `id_release`, `role_name`'
}
