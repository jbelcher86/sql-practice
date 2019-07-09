# !/usr/bin/env python2.7
import psycopg2

# Connect to db and create cursor
db = psycopg2.connect(dbname='news')
news_cursor = db.cursor()

# 'What are the most popular three articles of all time?
# Query is created as a string to be passed into the news_cursor
# substring(path) is used to allow a join between logs and articles
# on the slugs by eliminating the preceeding '/article/'.
pop_query = ('''
select title, number from
(select substring(path, 10), count(*) as number from log
where path !='/' group by path)
as views, articles where substring = slug
order by number desc limit 3;
''')

# Executing query on news db,
# and printing out the results of our query.
news_cursor.execute(pop_query)
pop_result = news_cursor.fetchall()
print 'What are the most popular three articles of all time?'
for title, views in pop_result:
    print '{} - {} views'.format(title, views)

# 'Who are the most popular article authors of all time?'
# Query is created as string to be passed into the news_cursor
# tables are once again joined on substring(path)=slug and
# author = author.id
pop_auth_query = ('''
select name, sum(number) as total from
(select name, author, title, number from
(select substring(path, 10), count(*) as number from log
where path !='/' group by path)
as hits, articles, authors
where substring = slug and author = authors.id
order by number desc)
as all_join
group by name order by total desc;
''')

# Executing query on news db,
# and printing out the results of our query.
news_cursor.execute(pop_auth_query)
auth_result = news_cursor.fetchall()
print 'Who are the most popular article authors of all time?'
for author, views in auth_result:
    print '{} - {} views'.format(author, views)

# On which days did more than 1% of requests lead to errors?
# Here we use the date_trunc function of postgres to truncate all dates
# to the day. Status = '404 NOT FOUND' is used to identify which requests
# resulted in errors.
error_query = ('''
select error_date, requests, http_error,
100.0 * http_error / requests as error_pct from
(select date_trunc('day', time) as request_date, count(*)
as requests from log group by request_date)
as hits,
(select date_trunc('day',time) as error_date, count(*)
as http_error from log where status = '404 NOT FOUND'
group by error_date)
as errors
where request_date = error_date
and errors.http_error > 0.01 * hits.requests
order by error_date desc;
''')

# Executing query on news db,
# and printing out the results of our query.
news_cursor.execute(error_query)
error_result = news_cursor.fetchall()
print 'On which days did more than 1% of requests lead to errors?'
for date, requests, errors, rate in error_result:
    print '{:%B %d, %Y} - {:.2f}% errors'.format(date, rate)

# close connection
db.close()
