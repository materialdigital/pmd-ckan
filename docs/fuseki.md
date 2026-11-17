# Fuseki in this stack

- Image: `secoresearch/fuseki:6.2.0` (Jena 6, Java 21), started with `FusekiServerCmd`.
- Access: everything except `/$/ping`, `/$/status` and static files requires the Fuseki `admin` login (`config/fuseki/shiro.ini.tpl`, copied to `/fuseki-base/shiro.ini` on every start by `config/fuseki/entrypoint.sh`). The public SPARQL access goes through the CKAN extension `ckanext-fuseki`.
- `compose.yaml` overrides `entrypoint:`, which makes Compose drop the image `CMD`, so `command:` is repeated there.
- `FUSEKI_JAVA_OPTS` (`.env`) must contain `-Dfuseki:allowAddByConfigFile=true`. `ckanext-fuseki` creates a dataset per CKAN dataset by posting an assembler description to `POST /$/datasets`; Fuseki 5.5+ rejects that unless this property is set (CVE-2025-50151 / CVE-2025-49656, admin-only upload of configuration with unvalidated paths). Accepted risk: Fuseki is only reachable for admins and by CKAN. See the `ckanext-fuseki` README, "Fuseki 5.x and 6.x".
- Datasets created as non-persistent are in memory and empty after a restart.
