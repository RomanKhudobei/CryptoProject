CREATE DATABASE IF NOT EXISTS coins;

USE coins;

CREATE TABLE IF NOT EXISTS coins (
	coin_id VARCHAR(15) PRIMARY KEY,
	entire_key VARCHAR(255),
	valid VARCHAR(1) DEFAULT 'X')
	DEFAULT CHARSET =  utf8;

CREATE INDEX validness ON coins (valid);

CREATE TABLE IF NOT EXISTS ips (
	ip VARCHAR(15) PRIMARY KEY,
	count SMALLINT DEFAULT 1,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
	DEFAULT CHARSET =  utf8;