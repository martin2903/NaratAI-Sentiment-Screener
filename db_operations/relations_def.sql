create table entryinfo(
entryid int primary key,
ticker varchar(5) not null,
headline varchar not null,
date_time timestamp not null,
url varchar unique not null
);

create table polaritywords(
entryid int references entryinfo(entryid),
words text[] not null,
sentiment_class text[] not null
);

create table sentiment(
entryid int references entryinfo(entryid),
overall_sent varchar not null,
sentiment_prob real[] not null
);

create table keyphrases(
entryid int references entryinfo(entryid),
phrases text[] not null
);

create table tickerinfo(
id int not null unique,
ticker varchar(5) primary key,
name varchar not null,
image_url varchar not null
);