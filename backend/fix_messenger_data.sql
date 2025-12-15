-- Fix empty messenger records in database
-- Run this to update existing records with empty arrays to empty objects

-- Update mail column
UPDATE messengers 
SET mail = '{}'::json 
WHERE mail IS NULL OR mail::text = '[]';

-- Update telegram column
UPDATE messengers 
SET telegram = '{}'::json 
WHERE telegram IS NULL OR telegram::text = '[]';

-- Update whatsapp column
UPDATE messengers 
SET whatsapp = '{}'::json 
WHERE whatsapp IS NULL OR whatsapp::text = '[]';

-- Update discord column
UPDATE messengers 
SET discord = '{}'::json 
WHERE discord IS NULL OR discord::text = '[]';

-- Verify the fix
SELECT id, mail, telegram, whatsapp, discord 
FROM messengers 
LIMIT 10;
