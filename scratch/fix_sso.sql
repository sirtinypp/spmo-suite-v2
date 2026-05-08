INSERT INTO socialaccount_socialapp (provider, name, client_id, secret, key, provider_id, settings) 
VALUES ('google', 'Google SSO', '[REDACTED]', '[REDACTED]', '', 'google', '{}') 
ON CONFLICT DO NOTHING;

INSERT INTO socialaccount_socialapp_sites (socialapp_id, site_id) 
SELECT id, 1 FROM socialaccount_socialapp WHERE provider = 'google' 
ON CONFLICT DO NOTHING;
