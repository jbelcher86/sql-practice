# README
Udacity Full Stack Web Developer Nanodegree

John Belcher

Project 1: Logs and Analysis

## Contents
udacity_1.py - source code

output.txt - output of running udacity_1.py

readme.md - this readme file

## Requirements
1. psycopg2 must be installed in order to connect to the newsdata db.
2. udacity_1.py must be run in the same folder as newsdata.sql

## Set Up Instructions

### Vagrant and VirtualBox
This project uses Vagrant and VirtualBox to run the Postgres database server.

#### VirtualBox
This project uses VirtualBox version 5.1.38, available [here](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1). VirtualBox allows us to spin up virtual machines running operating system such as Linux or Windows.

#### Vagrant
This project uses Vagrant 2.25, available [here](https://www.vagrantup.com/downloads.html). Vagrant keeps the installation and work environment of our virtual environment consistent, and allows us to share files between our local machine and the virtual one.

### Configuring and Starting the Virtual Machine

The virtual machine configuration can be downloaded [here](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip). Unzip this file and navigate to the new directory.

#### Acquring the Data
This project uses the newsdata.sql db, available [here](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip). Once downloaded, move newsdata.sql to the vagrant folder.

#### Starting the Virtual Machine
Once in the vagrant folder, start up Vagrant:
```bash
$ vagrant up
```
SSH into the VM:
```bash
$ vagrant ssh
```

#### Importing Data into the Database
Running the code require loading the data into a local database. This is accomplished by running the following command in the vagrant directory with newsdata.sql present:
```bash
psql -d news -f newsdata.sql
```

## Design
This program answers three questions using the newsdata.db, the psycopg2
package, and some built in postgres commands. Each query that is used to answer
these question is created as a string, and then passed into a cursor created in
the news db.

### Question 1: What are the most popular three articles of all time?

```sql
select title, number from
(select substring(path, 10), count(*) as number from log
where path !='/' group by path)
as views, articles where substring = slug
order by number desc limit 3;
```
The query which answers the first question uses data from the log and article tables.
The postgres command 'substring' is used to eliminate the leading characters '/article/' from the path column in the log table. This allows us to join these tables where that substring equals the slug associated with the article.

### Question 2: Who are the most popular article authors of all time?

```sql
select name, sum(number) as total from
(select name, author, title, number from
(select substring(path, 10), count(*) as number from log
where path !='/' group by path)
as hits, articles, authors
where substring = slug and author = authors.id
order by number desc)
as all_join
group by name order by total desc;
```

This query pulls data from all three tables in the news db, log, articles, and authors. Once again log and articles are joined on substring = slug, and articles and authors are joined on author = authors.id.

### Question 3: On which days did more than 1% of requests lead to errors?

```sql
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
```
This query takes place entirely in the log table. We use the date_trunc function in postgres to truncate all time data after the day (hours, minutes, seconds etc.). This allows us to easily count all requests that happen in one day. Logs where status = '404 NOT FOUND' are considered errors, and we report all days where the error rate is greater than 0.01.
## Running
When in the same directory as both newsdata.db and udacity_1.py:
```bash
vagrant@vagrant:/vagrant$ python udacity_1.py
```
This will result in the following output:
```text
What are the most popular three articles of all time?
Candidate is jerk, alleges rival - 338647 views
Bears love berries, alleges bear - 253801 views
Bad things gone, say good people - 170098 views
Who are the most popular article authors of all time?
Ursula La Multa - 507594 views
Rudolf von Treppenwitz - 423457 views
Anonymous Contributor - 170098 views
Markoff Chaney - 84557 views
On which days did more than 1% of requests lead to errors?
July 17, 2016 - 2.26% errors
```
