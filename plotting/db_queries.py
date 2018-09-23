DECADE_MASTER_DISTRIBUTION = """
  SELECT 
    concat(floor(m.year / 10) * 10, 's') as decade, 
    count(*) as count
  FROM 
    master m 
  GROUP BY 
    decade 
  ORDER BY 
    decade ASC 
"""

SIX_MOST_RECENT_MASTER_GENRES = """
    SELECT
        mg.genre_name as genre, 
        count(*) as master_count
    FROM
        master m
    INNER JOIN
        master_genre mg on mg.id_master = m.id_master
    GROUP BY
        mg.genre_name
    ORDER BY
        master_count desc
    LIMIT 
        6
"""

COMPOSITION_LENGTH_DISTRIBUTION = """
    SELECT
		case
			when c.length <= 90 then 'below90'
            when c.length > 90 and c.length <= 180 then 'below180'
            when c.length > 180 and c.length <= 240 then 'below240'
            when c.length > 240 and c.length <= 300 then 'below300'
            when c.length > 300 and c.length <= 360 then 'below360'
            when c.length > 360 then 'over360'
		end as category,
        count(*) as count
    FROM
        composition c 
	WHERE	
		c.length IS NOT NULL
	GROUP BY
		category
    ORDER BY
        c.length ASC
"""

CYR_LATIN_RATIO_PERCENTAGE = """
    SELECT 
        CASE
            when c.name REGEXP '[Α-Ωα-ωА-Яа-я]' then 'cyrilic'
            when c.name NOT REGEXP '[Α-Ωα-ωА-Яа-я]' then 'latin'
        END as kind,
        ROUND(count(*) / t.total_count * 100, 2) as count
    FROM
	composition as c
    LEFT JOIN
        (
            SELECT count(*) as total_count FROM composition 
        ) t on 1=1 
    GROUP BY
        kind
"""

CYR_LATIN_RATIO = """
    SELECT 
        CASE
            when c.name REGEXP '[Α-Ωα-ωА-Яа-я]' then 'cyrilic'
            when c.name NOT REGEXP '[Α-Ωα-ωА-Яа-я]' then 'latin'
        END as kind,
        count(*) as count
    FROM
	composition as c
    LEFT JOIN
        (
            SELECT count(*) as total_count FROM composition 
        ) t on 1=1 
    GROUP BY
        kind
"""

MASTER_GENRE_DISTRIBUTION = """
    SELECT
        CASE
            when t.genre_count = 1 then 'one_genre'
            when t.genre_count = 2 then 'two_genres'
            when t.genre_count = 3 then 'three_genres'
            when t.genre_count >= 4 then 'four_and_more_genres'
        END as kind,
        count(*) as count
    FROM
    (
        SELECT
            m.*, 
            count(*) as genre_count
        FROM
            master m 
        INNER JOIN
            master_genre mg on mg.id_master = m.id_master
        GROUP BY
            m.id_master
    ) t
    GROUP BY
        kind
"""

MASTER_GENRE_DISTRIBUTION_PERCENTAGE = """
    SELECT
        CASE
            when t.genre_count = 1 then 'one_genre'
            when t.genre_count = 2 then 'two_genres'
            when t.genre_count = 3 then 'three_genres'
            when t.genre_count >= 4 then 'four_and_more_genres'
        END as kind,
        ROUND(count(*) / t2.total_count * 100,  2) as count
    FROM
        (
            SELECT
                m.*, 
                count(*) as genre_count
            FROM
                master m 
            INNER JOIN
                master_genre mg on mg.id_master = m.id_master
            GROUP BY
                m.id_master
        ) t
    LEFT JOIN
        (
            SELECT 
                count(distinct mg.id_master) as total_count 
            FROM 
                master_genre mg
        ) t2 on 1=1
    GROUP BY
        kind
"""