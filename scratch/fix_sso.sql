INSERT INTO socialaccount_socialapp (provider, name, client_id, secret, key, provider_id, settings) 
VALUES ('google', 'Google SSO', '307307846379-hk1atfjhev4p84fdicmglhl57jik0cn7.apps.googleusercontent.com', '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', '', 'google', '{}') 
ON CONFLICT DO NOTHING;

INSERT INTO socialaccount_socialapp_sites (socialapp_id, site_id) 
SELECT id, 1 FROM socialaccount_socialapp WHERE provider = 'google' 
ON CONFLICT DO NOTHING;
