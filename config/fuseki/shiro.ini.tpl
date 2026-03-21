# Licensed under the terms of http://www.apache.org/licenses/LICENSE-2.0

[main]
# Development
ssl.enabled = false

plainMatcher=org.apache.shiro.authc.credential.SimpleCredentialsMatcher
#iniRealm=org.apache.shiro.realm.text.IniRealm
iniRealm.credentialsMatcher = $plainMatcher

#localhostFilter=org.apache.jena.fuseki.authz.LocalhostFilter

[users]
# Implicitly adds "iniRealm =  org.apache.shiro.realm.text.IniRealm"
admin=placeholder

[roles]

[urls]
## Control functions open to anyone (health checks)
/$/status = anon
/$/ping   = anon

## Allow the UI to load without auth (Vue SPA + static assets)
/static/** = anon
/ = authcBasic,user[admin]

## Admin and all data endpoints require HTTP Basic Auth
/$/** = authcBasic,user[admin]
/** = authcBasic,user[admin]
