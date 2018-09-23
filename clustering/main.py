import sys

sys.path.append('../')

import numpy as np
import constants as cn

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
from db_util import DbUtil

OPTIONS = {
    "year": "> Release Year (y/n): ",
    "rating": "> Release Rating (y/n): ",
    "genre": "> Release Genres (y/n): ",
    "style": "> Release Styles (y/n): "
}


def select_options(options):
    opt_k = int(input("> K = "))
    opt_features = []

    print("Features:")
    for k, v in options.items():
        opt = input(v)
        if opt == 'y':
            opt_features += [k]

    if opt_features.__len__() == 0 or opt_k <= 0:
        raise Exception('No features selected!')

    return opt_k, opt_features


def create_db_query(opt_features, min, max):
    query = """
        SELECT 
            IFNULL(CAST((r.rating / 5) AS DECIMAL(10,6)), -1) as rating,
            IFNULL(CAST(((r.year - {MIN_Y}) / ({MAX_Y} - {MIN_Y})) AS DECIMAL(10,6)), -1) as year
            {SELECT_FIELDS}
        FROM discogs.release as r
        {GENRE_JOIN}
        {STYLE_JOIN}
        GROUP BY r.id_release
    """

    select_fields = ''
    if 'genre' in opt_features and 'style' in opt_features:
        select_fields = ",concat( group_concat(distinct rg.genre_name), ' ',group_concat(distinct rs.style_name)) as text"
    elif 'genre' in opt_features:
        select_fields = ",group_concat(distinct rg.genre_name) as text"
    elif 'style' in opt_features:
        select_fields = ",group_concat(distinct rs.style_name) as text"

    genre_join = 'INNER JOIN discogs.release_genre rg on rg.id_release = r.id_release ' if 'genre' in opt_features else ''
    style_join = 'INNER JOIN discogs.release_style rs on rs.id_release = r.id_release' if 'style' in opt_features else ''

    return query.format(SELECT_FIELDS=select_fields, GENRE_JOIN=genre_join, STYLE_JOIN=style_join, MIN_Y=min, MAX_Y=max)


def create_min_max_year_query():
    return "select min(r.year) as _min, max(r.year) as _max from discogs.release as r"


def main():
    try:

        opt_k, opt_features = select_options(OPTIONS)
        db = DbUtil(host=cn.DB_HOST, user=cn.DB_USER, password=cn.DB_PASS, database=cn.DB_DATABASE)

        min_max = db.execute(create_min_max_year_query())[0]
        min, max = min_max.get('_min'), min_max.get('_max')

        query = create_db_query(opt_features, min, max)

        result = db.execute(query)

        # bag of words
        if opt_features.__contains__('genre') or opt_features.__contains__('style'):

            vectorizer = CountVectorizer(binary=True)
            vectorizer.fit_transform([r['text'] for r in result])

            for r in result:
                r['text'] = vectorizer.transform([r['text']]).toarray()[0]
                if 'year' in opt_features:
                    r['text'] = np.append(r['text'], r['year'])
                if 'rating' in opt_features:
                    r['text'] = np.append(r['text'], r['rating'])

        # year or rating selected only
        else:

            for r in result:
                if 'year' in opt_features and 'rating' in opt_features:
                    r['text'] = np.array([r['year'], r['rating']])
                elif 'year' in opt_features:
                    r['text'] = np.array([r['year']])
                else:
                    r['text'] = np.array([r['rating']])

        x_train = [r['text'] for r in result]

        model = KMeans(n_clusters=opt_k, random_state=0)
        model.fit(x_train)

    except Exception as e:
        print("Error code: {err_code}".format(err_code=str(e)))


if __name__ == '__main__':
    main()
