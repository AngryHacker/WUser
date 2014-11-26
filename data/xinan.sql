drop database if exists `xinan`;

create database `xinan`
	default character set utf8
	default collate utf8_general_ci;

use xinan;

drop table if exists `users`;
CREATE TABLE users
(
	`user_id` INTEGER NOT NULL AUTO_INCREMENT comment '主键',
	`nickname` VARCHAR(128) NOT NULL comment '微博昵称',
	`url` VARCHAR(256) NOT NULL comment '主页url',
	`is_evil` tinyint not null default 0 comment '是否恶意用户',
	primary key (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 comment='微博用户';

drop table if exists `fans`;
CREATE TABLE `fans`
(
	`f_id` INTEGER NOT NULL AUTO_INCREMENT comment '主键',
    `user1` INTEGER not null comment '关注人',
    `user2` INTEGER not null comment '被关注者',
	CONSTRAINT `fr_ibfk_1` FOREIGN KEY (`user1`)
		REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT `fr_ibfk_2` FOREIGN KEY (`user2`)
		REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
	primary key (`f_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 comment='关注表';

drop table if exists `post`;
CREATE TABLE post
(
	`post_id` INTEGER NOT NULL AUTO_INCREMENT comment '主键',
	`content` TEXT NOT NULL comment '微博',
	`post_time` INTEGER not null comment '发表时间',
	`user_id` INTEGER NOT NULL comment '发布者',
	CONSTRAINT `post_ibfk_1` FOREIGN KEY (user_id)
		REFERENCES users(`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
	primary key (`post_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 comment='微博内容表';

