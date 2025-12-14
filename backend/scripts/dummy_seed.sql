-- dummy_seed.sql
-- Seed data for PurplePatch Messenger Service

-- 1. Create Messengers
INSERT INTO messengers (id, mail, whatsapp, telegram, discord, created_at, modified_at) VALUES
(1, '["john@example.com"]', '["+1234567890"]', '["@john_doe"]', '["john#1234"]', NOW(), NOW()),
(2, '["alice@example.com"]', '[]', '["@alice_wonder"]', '[]', NOW(), NOW()),
(3, '["bob@builder.com", "bob.work@builder.com"]', '["+0987654321"]', '[]', '["bob_builds#9999"]', NOW(), NOW());

-- 2. Create Subscriptions
-- Removed % symbol to avoid SQLAlchemy text() interpolation issues
INSERT INTO subscriptions (id, name, type, time, offer, prize, remark, current_subs_quantity, created_at, modified_at) VALUES
(1, 'Starter Pack', 'Standard', 'Monthly', '10 percent off first month', 'None', '[]', 1, NOW(), NOW()),
(2, 'Pro Gamer', 'Premium', 'Yearly', 'Free headset', 'Gaming Chair', '["Best Value"]', 1, NOW(), NOW()),
(3, 'Logic Master', 'Logic', 'Lifetime', 'No Ads', 'Trophy', '[]', 0, NOW(), NOW());

-- 3. Create Users
INSERT INTO users (id, username, full_name, email, phone_number, quiz_ids, messenger_id, subscription_id, created_at, modified_at) VALUES
(1, 'johndoe', 'John Doe', 'john@example.com', '+1234567890', '[]', 1, NULL, NOW(), NOW()),
(2, 'alicew', 'Alice Wonderland', 'alice@example.com', NULL, '[]', 2, NULL, NOW(), NOW()),
(3, 'bobthebuilder', 'Bob Builder', 'bob@builder.com', '+0987654321', '[]', 3, NULL, NOW(), NOW());

-- 4. User Subscribed
INSERT INTO user_subscribed (user_id, subs_id, created_at, modified_at) VALUES
(1, 1, NOW(), NOW()),
(2, 2, NOW(), NOW());

-- 5. Quizzes
INSERT INTO quizzes (user_id, subs_id, score, time, created_at, modified_at) VALUES
(1, 1, 45, 120, NOW(), NOW()),
(1, 1, 10, 30, NOW(), NOW()),
(2, 2, 80, 200, NOW(), NOW());

-- 6. Messages
INSERT INTO messages (messenger_type, text, link, time, created_at, modified_at) VALUES
('MAIL', 'Welcome to the Starter Pack!', NULL, NOW(), NOW(), NOW()),
('WHATSAPP', 'Your quiz score is 45. Keep it up!', 'http://example.com/quiz/1', NOW(), NOW(), NOW()),
('TELEGRAM', 'Alice, you are crushing it!', NULL, NOW(), NOW(), NOW());
