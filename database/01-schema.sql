DROP DATABASE IF EXISTS instagram_sponsor_tracker;
CREATE DATABASE instagram_sponsor_tracker;
USE instagram_sponsor_tracker;

CREATE TABLE IF NOT EXISTS users (
  id bigint UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(32) NOT NULL,
  fullname VARCHAR(32) NOT NULL,
  followers_count INT(4) UNSIGNED NOT NULL,
  account_type INT(4) UNSIGNED NOT NULL,
  is_business_account BOOLEAN DEFAULT NULL,
  is_verified BOOLEAN DEFAULT NULL,
  is_private BOOLEAN DEFAULT NULL,
  profile_pic_url LONGTEXT DEFAULT NULL,
  updated_at DATETIME DEFAULT NULL,
  activated BOOLEAN DEFAULT 0 NOT NULL
);

CREATE TABLE IF NOT EXISTS ad_statuses (
  id INT(4) NOT NULL PRIMARY KEY,
  status VARCHAR(32) NOT NULL
);

INSERT INTO ad_statuses(id, status) VALUES(-2, 'scam_ad');
INSERT INTO ad_statuses(id, status) VALUES(-1, 'hidden_ad');
INSERT INTO ad_statuses(id, status) VALUES(0, 'no_ad');
INSERT INTO ad_statuses(id, status) VALUES(1, 'incorrectly_flagged_ad');
INSERT INTO ad_statuses(id, status) VALUES(2, 'legit_ad');

CREATE TABLE IF NOT EXISTS posts (
  id VARCHAR(32) NOT NULL PRIMARY KEY,
  type ENUM('post', 'reel') NOT NULL,
  code VARCHAR(32) DEFAULT NULL,
  taken_at DATETIME NOT NULL,
  location LONGTEXT DEFAULT NULL,
  lat DECIMAL(10, 8) DEFAULT NULL,
  lng DECIMAL(11, 8) DEFAULT NULL,
  is_paid_partnership BOOLEAN NOT NULL,
  user_id bigint UNSIGNED NOT NULL,
  description LONGTEXT DEFAULT NULL,
  ad_status_id INT(4) NOT NULL,
  submitted BOOLEAN DEFAULT 0 NOT NULL,
  expiring_at DATETIME DEFAULT NULL,
  CONSTRAINT `post_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `post_ad_status_id` FOREIGN KEY (`ad_status_id`) REFERENCES `ad_statuses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS medias (
  id INT(4) AUTO_INCREMENT PRIMARY KEY,
  post_id VARCHAR(32) NOT NULL,
  content_url LONGTEXT NOT NULL,
  ocr_text LONGTEXT DEFAULT NULL,
  CONSTRAINT `media_post_id` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS keywords (
  id INT(4) UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY,
  keyword VARCHAR(32) NOT NULL,
  ad_status_id INT(4) NOT NULL,
  CONSTRAINT `keyword_ad_status_id` FOREIGN KEY (`ad_status_id`) REFERENCES `ad_statuses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

FLUSH PRIVILEGES;
CREATE USER 'instagram_sponsor_tracker'@'localhost' IDENTIFIED BY 'instagram_sponsor_tracker*$14352!';
GRANT ALL PRIVILEGES ON *.* TO 'instagram_sponsor_tracker'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
