CREATE TABLE hn_feed (
  itemid SERIAL PRIMARY KEY,
  published TIMESTAMP NOT NULL,
  title TEXT NOT NULL,
  link TEXT NOT NULL,
  comments TEXT NOT NULL,
  link_digest TEXT NOT NULL,
  comments_digest TEXT NOT NULL,
  feed JSON NOT NULL
);

CREATE INDEX hn_feed_published_idx ON hn_feed (published);
CREATE UNIQUE INDEX hn_feed_link_digest_uniq_idx ON hn_feed (link_digest);
CREATE INDEX hn_feed_comments_digest_idx ON hn_feed (comments_digest);
