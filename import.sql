CREATE DATABASE IF NOT EXISTS crypto_project;

USE crypto_project;

CREATE TABLE IF NOT EXISTS coins (
	coin_id VARCHAR(15) PRIMARY KEY,
	entire_key VARCHAR(255),
	valid VARCHAR(1) DEFAULT 'X')
	DEFAULT CHARSET = utf8;

CREATE INDEX validness ON coins (valid);

CREATE TABLE IF NOT EXISTS ips (
	ip VARCHAR(15) PRIMARY KEY,
	count SMALLINT DEFAULT 1,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
	DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS transactions (
	TxHash VARCHAR(66), 
	Block INT, 
	Age DATETIME, 
	TxFrom VARCHAR(42), 
	TxTo VARCHAR(42), 
	Value VARCHAR(20),
	PRIMARY KEY ( TxHash, Block, Age ))
	DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS log (
	TxHash VARCHAR(100), 
	Block INT, 
	Age DATETIME, 
	TxFrom TEXT, 
	TxTo TEXT, 
	Value TEXT,
	ErrorCode TINYINT,
	ErrorDescription TEXT,
	INDEX log_index (ErrorCode, Age, Block, TxHash))
	DEFAULT CHARSET = utf8;