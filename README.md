# PMD-CKAN

This composition of applications provides a solution for hosting material science data for projects in the material digital initiative to participate in a decentralized linked data space with a central data portal instance. It also features an ontology agnostic transformation pipeline and a triple store integration.

## Features

- Central Component is a [CKAN](https://ckan.org/) 2.12 instance as data management system, with default views for pdf, images, text, csv, html, markdown.
- A [apche jena fuseki](https://jena.apache.org/documentation/fuseki2/) triple store at a sublocation /fuseki
- A plugin to create accompanying named graphs in jena fuseki for semantic data contained in ckan datasets including sparql endpoint publication and a user-friendly sparql query interface known as [sparklis](https://github.com/sebferre/sparklis)
- a pipeline for transforming complex csv data common in the domain to [csvw metadata](https://www.w3.org/ns/csvw)
- A rule based mapping pipeline to combine rdf containing data with knowledge graphs to represent material data, its measurement routine and the processing. A tutorial and the steps involved can be found [here](https://github.com/Mat-O-Lab/IOFMaterialsTutorial).

## Prerequisites

Before you begin, make sure you have the following installed:

- Docker
- Docker Compose

## Installation

1. Clone this repository to your local machine and init submoduls:
    ```bash
    git clone https://github.com/materialdigital/pmd-ckan.git
    git submodule update --init
    ```

2. Navigate to the pmd-ckan directory:
    ```bash
    cd pmd-ckan
    ```

3. create a .env file, use [example.env](config/example.env) as a template

    **all variables starting with CKANINI__ will be translated to the ckan.ini removing CKANINI__, replacing "__" with "."  and putting the name to lowercase**
    examples:
    CKANINI__CSVTOCSVW__FORMATS -> csvtocsvw.formats 
    CKANINI__CSVTOCSVW__SSL_VERIFY -> csvtocsvw.ssl_verify 

4. replace all values in <> braces or are comented to be changed
5. make changes according to your ssl or proxy configuration in [config/nginx/default.conf.template](config/nginx/default.conf.template)
6. Run the docker compose stack, it will pull and build the necessary containers
    ```bash
    docker compose up
    ```
7. After first successful startup, login into ckan with the admin password you defined in your .env

8. The API token for the background tasks (csvtocsvw, csvwmapandtransform, fuseki) is generated automatically on every start of the ckan container (prod and dev) and written to ckan.ini; the tokens of earlier starts are revoked. Without it these services cannot read private datasets (HTTP 403) ([config/ckan/02_backgroundjobs.sh](config/ckan/02_backgroundjobs.sh)). No manual token or restart is needed.

## Database
The stack runs PostgreSQL 16 (`postgres:16-alpine`). Upgrading from older instances (13+): see [docs/postgres-upgrade.md](docs/postgres-upgrade.md).

## Theme
The CKAN theme comes from [ckanext-matolabtheme](https://github.com/Mat-O-Lab/ckanext-matolabtheme) and works with both CKAN base
themes. The classic theme is the default; for the CKAN 2.12 opt-in **midnight-blue** theme (default of CKAN 3.0) set in `.env`:

```bash
CKANINI__CKAN__BASE_PUBLIC_FOLDER=public-midnight-blue
CKANINI__CKAN__BASE_TEMPLATES_FOLDER=templates-midnight-blue
```

Keep `CKANINI__CKAN__SITE_LOGO` and `CKANINI__CKAN__FAVICON` as relative paths (`/static/Logo.svg`), as in
[config/example.env](config/example.env): an absolute `${CKAN_SITE_URL}/...` URL breaks the logo when you open the site with a
different scheme or hostname (self-signed certificate). More in the extension's README.

## Single sign-on (optional)
Users can log in through an OpenID Connect provider such as Keycloak with [ckanext-sso](https://github.com/Mat-O-Lab/ckanext-sso) (already part of the `CKAN__PLUGINS` list):

1. Register a client at your provider and allow `${CKAN_SITE_URL}/dashboard` as redirect URL.
2. Fill in the `EXTENSION: SSO` block of your `.env` (see [config/example.env](config/example.env)): realm, host, client id and secret.
3. On login the `groups` claim of the provider is matched with the **names** of your CKAN organizations and groups; matching users are added with the role from `CKANINI__CKANEXT__SSO__ROLE` (default `member`).
4. New users get their CKAN username from the claim set in `CKANINI__CKANEXT__SSO__PROFILE_USERNAME_FIELD` (default `preferred_username`, then `name`); existing users are matched by email.
5. An LDAP department lookup is available but off unless `CKANINI__CKANEXT__SSO__LDAP_SERVER` is set. All options are described in the [ckanext-sso README](https://github.com/Mat-O-Lab/ckanext-sso#configuration).

## Container images
Services that are not CKAN itself run from images pinned in [compose.yaml](compose.yaml), so a `docker compose pull` never changes the stack silently:

| Service | Image | Notes |
|---|---|---|
| csvtocsvw | `ghcr.io/mat-o-lab/csvtocsvw:v1.3.6` | |
| maptomethod | `ghcr.io/mat-o-lab/maptomethod:v1.1.7` | |
| rdfconverter, yarrrml-parser, rmlmapper | `ghcr.io/mat-o-lab/{rdfconverter,yarrrml-parser,rmlmapper-webapi}:v1.3.4` | released together from [Mat-O-Lab/RDFConverter](https://github.com/Mat-O-Lab/RDFConverter): keep the three tags identical |
| fuseki | built from [config/fuseki/Dockerfile](config/fuseki/Dockerfile) | upstream Dockerfile on a current temurin base, Jena 6.2.0 (6.3.0 breaks `ckanext-fuseki`), see [docs/fuseki.md](docs/fuseki.md) |
| solr, sparklis | built from `config/solr/`, `config/sparklis/` | current bases |
| nginx, redis | `nginx:1.30-alpine`, `redis:7-alpine` | |

To upgrade a mat-o-lab image, change the tag in `compose.yaml`, `docker compose pull`, run [scripts/scan-images.sh](scripts/scan-images.sh) and
recreate the service. The images built here (ckan, db, solr, sparklis, fuseki) must be built (`docker compose build --pull`) before the scan can include them.

## Vulnerability scan
[scripts/scan-images.sh](scripts/scan-images.sh) scans every image of the compose stack with [Trivy](https://trivy.dev) (run as a
container, nothing to install) and audits the Python packages of the ckan image with `pip-audit`:

```bash
scripts/scan-images.sh                 # HIGH and CRITICAL findings that have a fix
scripts/scan-images.sh -a -f CRITICAL  # include unfixed findings, exit 1 if any CRITICAL is left
scripts/scan-images.sh -f CRITICAL -g '^(nginx|datastack_dev-ckan)'   # only the matching images may fail the run
```

Reports (one JSON per image and `summary.md`) are written to `reports/security/<timestamp>/` (git-ignored). Findings in a base
image are closed by updating the tag or rebuilding (see [config/sparklis/Dockerfile](config/sparklis/Dockerfile) and
[config/solr/Dockerfile](config/solr/Dockerfile) for images built on a current base). Findings you accept for now belong in a
local, git-ignored `.trivyignore.yaml` with a reason and an expiry date each; the template is
[scripts/trivyignore.example.yaml](scripts/trivyignore.example.yaml). Results change daily as new advisories appear, so rebuild with
`docker compose build --pull` and rescan regularly.

## Config Option
Debug and Development Mode
```bash
docker compose -f compose.yaml -f compose.dev.yaml up -d
```
CKAN plugins in folder ./ckan_plugins will be shared to the ckan container and the server reloads on changes to files for extention test adn development.

### Switching between dev and prod (volume permissions)
The dev and the prod ckan container share the named volume `ckan_storage` (uploads and the web asset cache), but they run
CKAN as different users: the **prod image runs CKAN as uid 503** (`ckan:ckan-sys`, gid 502), the **dev container remaps
`ckan` to the owner of `./ckan_plugins`** (usually your host uid, e.g. 1000). After running dev, a prod start can therefore
fail on every page with

```
PermissionError: [Errno 13] Permission denied: '/var/lib/ckan/webassets/.webassets-cache/...'
```

Fix it once by giving the volume to the prod user (only ownership changes, no file contents):

```bash
docker run --rm -v <project>_ckan_storage:/v alpine chown -R 503:502 /v   # <project> is the compose project, e.g. datastack_dev
```

Going from prod to dev needs nothing: the dev entrypoint ([config/ckan/entrypoint_wrapper.sh](config/ckan/entrypoint_wrapper.sh)) remaps
the user and fixes the ownership on start. Never run `ckan` commands in the container as root (`docker exec -u ckan ...`),
because root-owned cache files cause the same error.

### Updating the extensions
The extensions are installed from PyPI with `>=` pins in [config/ckan/Dockerfile](config/ckan/Dockerfile); `ckanext-harvest`,
`ckanext-citeproc` and `ckanext-excelforms` are not on PyPI (or too old) and are installed from Git **pinned to a commit**, so a
build never changes silently. To pick up new releases rebuild the image with `docker compose up -d --build`; to update a
Git-installed extension change the commit in the Dockerfile.
      
# Acknowledgments
The authors would like to thank the Federal Government and the Heads of Government of the Länder for their funding and support within the framework of the [Platform Material Digital](https://www.materialdigital.de) consortium. Funded by the German [Federal Ministry of Education and Research (BMBF)](https://www.bmbf.de/bmbf/en/) through the [MaterialDigital](https://www.bmbf.de/SharedDocs/Publikationen/de/bmbf/5/31701_MaterialDigital.pdf?__blob=publicationFile&v=5) Call in Project [KupferDigital](https://www.materialdigital.de/project/1) - project id 13XP5119.
