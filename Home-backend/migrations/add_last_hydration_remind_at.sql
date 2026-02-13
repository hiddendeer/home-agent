-- 添加 last_hydration_remind_at 字段到 users 表
-- 执行方式：mysql -u your_user -p your_database < migrations/add_last_hydration_remind_at.sql

ALTER TABLE users
ADD COLUMN last_hydration_remind_at DATETIME NULL COMMENT '上次喝水提醒时间'
AFTER is_superuser;
