# PostgreSQL in the stack and upgrade path

## What is in use

| Item | Value |
|------|-------|
| Service | `db` in [compose.yaml](../compose.yaml) / [compose.dev.yaml](../compose.dev.yaml) |
| Image | built from [ckan-docker/postgresql/Dockerfile](../ckan-docker/postgresql/Dockerfile) = `postgres:16-alpine` (currently 16.x) |
| Data | named volume `pg_data` -> `/var/lib/postgresql/data` (compose project prefix, e.g. `datastack_dev_pg_data`) |
| Databases | `ckan` (CKAN), `datastore` (DataStore), `ckan_test`/`datastore_test` (test). Created by init scripts in `ckan-docker/postgresql/docker-entrypoint-initdb.d/` |
| Roles | admin from `POSTGRES_USER`, CKAN user `CKAN_DB_USER`, read-only `DATASTORE_READONLY_USER` |

The image tag comes from the `ckan-docker` submodule. History there: 9.6 -> 12 -> 14 -> **16**. CKAN 2.12 runs fine on 16.

**Important:** the init scripts run only on an *empty* data dir. Pointing PG 16 at a PG 13 data dir does NOT work (`database files are incompatible with server`). A major-version upgrade needs dump/restore or `pg_upgrade`.

## Upgrade path from PG 13 (also 14, 15) to 16

Direct jump 13 -> 16 is supported. No need to step through 14/15.

Recommended order: **upgrade PG first (while old CKAN still works), verify, then upgrade CKAN** — or at least do not do both in one step, so failures are attributable.

### Method A: dump and restore (recommended)

Simple, safe, works across any versions. Downtime = dump + restore time.

1. Stop everything except the DB, back up volume as well:
   ```bash
   docker compose stop ckan nginx   # and any other service that touches db (supervisor/worker are inside ckan)
   docker run --rm -v <old_project>_pg_data:/v -v "$PWD":/b alpine tar czf /b/pg_data_backup.tgz -C /v .
   ```
2. Dump from the OLD running db container (roles + all databases):
   ```bash
   docker compose exec -T db pg_dumpall -U "$POSTGRES_USER" > pg_dumpall.sql
   ```
   Check the file is non-empty and ends with `PostgreSQL database cluster dump complete`.
3. Stop stack, remove old volume (backup from step 1 is the fallback):
   ```bash
   docker compose down
   docker volume rm <project>_pg_data
   ```
4. Start only the new PG 16 container **without init scripts clobbering the restore**. Easiest: let init scripts run on the empty volume, then drop and restore over it:
   ```bash
   docker compose up -d --build db
   docker compose exec -T db psql -U "$POSTGRES_USER" -d postgres -f - < pg_dumpall.sql
   ```
   Errors like `role "ckan" already exists` / `database "ckan" already exists` are expected and harmless (roles/DBs created by init scripts; data still loads). To avoid noise, instead start a plain `postgres:16-alpine` against the empty volume with only `POSTGRES_PASSWORD` set, restore, then switch back to compose.
5. **Re-set role passwords (required when coming from PG 13).** PG 13 stores `md5` hashes; `pg_dumpall` restores them, but the PG 16 image only accepts `scram-sha-256` on network connections (`host all all all scram-sha-256`). Without this step CKAN fails with `password authentication failed for user "<CKAN_DB_USER>"`.
   ```bash
   docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -v ON_ERROR_STOP=1 <<EOF
   SET password_encryption = '"'"'scram-sha-256'"'"';
   ALTER ROLE "$POSTGRES_USER" PASSWORD '"'"'$POSTGRES_PASSWORD'"'"';
   ALTER ROLE "$CKAN_DB_USER" PASSWORD '"'"'$CKAN_DB_PASSWORD'"'"';
   ALTER ROLE "$DATASTORE_READONLY_USER" PASSWORD '"'"'$DATASTORE_READONLY_PASSWORD'"'"';
   EOF'
   ```
   Check: `select rolname, left(rolpassword,14) from pg_authid;` must show `SCRAM-SHA-256$`.
6. Start the whole stack:
   ```bash
   docker compose up -d
   ```
7. Post checks:
   ```bash
   docker compose exec db psql -U "$POSTGRES_USER" -c "select version();"
   docker compose exec ckan ckan -c /srv/app/ckan.ini db version      # expect "(head)"
   ```
   Open a dataset with a DataStore resource and run a `datastore_search` call.

**Tested** (CKAN 2.12.1 prod compose, fresh stack on `postgres:13-alpine` with 1 org, 3 datasets, 1 DataStore table, then Method A to `postgres:16-alpine`): row counts, alembic head (`9445ce34fc23`), DataStore content and text sort order identical before/after; new dataset created after migration. `db init` and `db upgrade` are not needed: the dump already carries the CKAN schema, and `ckan db version` reports head. Run `ckan db upgrade` only when coming from an older CKAN.

### Method B: pg_upgrade (large DBs, less downtime)

Uses hard links (`--link`) so it is fast, but needs both binaries. Use a helper image such as `tianon/postgres-upgrade:13-to-16` (Debian based).

```bash
docker compose down
# backup volume first (step 1 above) — --link makes rollback impossible once new cluster started
docker run --rm \
  -v <project>_pg_data:/var/lib/postgresql/old/data \
  -v <project>_pg_data_new:/var/lib/postgresql/new/data \
  tianon/postgres-upgrade:13-to-16 --link
```
**Also re-set passwords as in Method A step 5** (pg_upgrade keeps md5 hashes). Then mount `pg_data_new` as `pg_data` (or copy contents over), copy the old `pg_hba.conf` settings if customised, start the 16 container, and run:
```bash
docker compose exec db vacuumdb -U "$POSTGRES_USER" --all --analyze-in-stages
```
Caveat: the helper image is Debian (glibc), the stack image is Alpine (musl) -> see below.

### Alpine / collation note (13 -> 16 on `-alpine` images)

If your old instance was a **Debian-based** image (`postgres:13`) and the new one is `postgres:16-alpine`, string sorting (collation) differs (glibc vs musl). Indexes on text columns can then be wrong (missing rows in lookups, unique violations not detected). Fix after restore/upgrade:
```bash
docker compose exec db psql -U "$POSTGRES_USER" -d ckan       -c "REINDEX DATABASE ckan;"
docker compose exec db psql -U "$POSTGRES_USER" -d datastore  -c "REINDEX DATABASE datastore;"
```
With dump/restore (Method A) indexes are rebuilt on load, so this is only needed for Method B. If old instance was already `-alpine`, skip.

### After the DB: CKAN 2.12 migration

```bash
docker compose exec ckan ckan -c /srv/app/ckan.ini db upgrade
docker compose exec ckan ckan -c /srv/app/ckan.ini search-index rebuild   # only if Solr volume was reset
```
If DataStore permissions are lost (read-only user cannot read), re-run:
```bash
docker compose exec ckan ckan -c /srv/app/ckan.ini datastore set-permissions | docker compose exec -T db psql -U "$POSTGRES_USER" --set ON_ERROR_STOP=1
```

### Rollback

- Method A: restore `pg_data_backup.tgz` into a fresh volume, switch image tag back to the old version.
- Method B with `--link`: only possible from the backup taken before the upgrade.

### Future major upgrades

Same procedure: bump the tag in the submodule Dockerfile (or override), take dump with the OLD container, restore into the NEW one. Always dump with the old server, restore with the new one.
