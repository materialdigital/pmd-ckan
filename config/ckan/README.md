# CKAN Docker Configuration

This directory contains custom CKAN Docker configurations that override the default `ckan-docker` repository files.

## Files Overview

### Dockerfiles

- **`Dockerfile`** - Production build configuration
- **`Dockerfile.dev`** - Development build configuration

### Scripts

- **`start_ckan.sh`** - Main CKAN startup script
- **`entrypoint_wrapper.sh`** - Dev mode permission wrapper
- **`03_harvest.sh`** - Harvest plugin initialization
- **`04_supervisor.sh`** - Supervisor daemon startup

### Configuration

- **`supervisor-ckan-worker.conf`** - Background worker configuration
- **`dcatde_themes.json`** - DCAT-DE theme definitions
- **`example.env`** - Environment variable template

## Dockerfile Differences

### Production (`Dockerfile`)

**Purpose:** Optimized for production deployment

**Key Features:**
- Installs extensions from PyPI where available (stable versions)
- Uses GitHub direct installs for packages not on PyPI or requiring specific branches
- Non-editable installations (smaller image size)
- Faster builds with better layer caching
- No development repositories

**Extensions Installed:**
- Core: csvtocsvw, csvwmapandtransform, fuseki, pdfview, multiuploadform, sso, markdown-view
- Theme: matolabtheme
- Forms: excelforms
- Metadata: scheming, harvest, dcat
- Citations: citeproc

### Development (`Dockerfile.dev`)

**Purpose:** Development environment with editable extensions

**Key Features:**
- Creates Python virtual environment at `/srv/app/.local`
- Installs extensions as editable (`-e git+https://...`)
- Allows live code changes to extensions
- Includes additional dev-only extensions (markdown_view from custom fork)
- Larger image size due to git repositories

**Additional Setup:**
- UWSGI installed for development server
- Virtual environment for isolated dependencies
- Editable installs for active development

## Extension Installation Methods

### Production

**From PyPI (preferred):**
```dockerfile
RUN pip3 install --no-cache-dir ckanext-example
```

**From GitHub (when not on PyPI or need specific branch):**
```dockerfile
RUN pip3 install --no-cache-dir \
    git+https://github.com/org/ckanext-example.git#egg=ckanext-example
```

### Development

**Editable installs from GitHub:**
```dockerfile
RUN pip3 install -e git+https://github.com/org/ckanext-example.git#egg=ckanext-example && \
    pip3 install -r https://raw.githubusercontent.com/org/ckanext-example/main/requirements.txt
```

## Maintenance Notes

### Adding New Extensions

**For Production:**
1. Add package name to appropriate section in `Dockerfile`
2. Use `--no-cache-dir` flag
3. Group related extensions together

**For Development:**
1. Add editable install to `Dockerfile.dev`
2. Include requirements.txt installation
3. Maintain same grouping as production file

### Version Pinning

- **Production:** Use PyPI version specifiers (e.g., `==1.0.8`)
- **Development:** Use git commit hashes for reproducibility (e.g., `@27035f4d5b`)

### Updating Extensions

**Production:**
```bash
# Simply update version in Dockerfile
ckanext-fuseki==1.0.9
```

**Development:**
```bash
# Update git URL or commit hash
git+https://github.com/org/ckanext-example.git@v2.0.0#egg=ckanext-example
```

## Build Context

Both Dockerfiles are designed to work with the build context set to `ckan-docker/ckan/`:

```yaml
build:
  context: ckan-docker/ckan/
  dockerfile: ../../config/ckan/Dockerfile
```

This maintains compatibility with the upstream `ckan-docker` repository structure while allowing custom configurations in the `config/ckan/` directory.

## Citation Styles

Both Dockerfiles download citation style language (CSL) files to `/srv/app/cls/`:
- aci-materials-journal.csl
- advanced-engineering-materials.csl
- advanced-science.csl

Add more styles by updating the `CLSS` environment variable in the Dockerfile.

## Removed Items

The following items were cleaned up in the latest revision:
- ❌ Duplicate `ckanext-scheming` installations
- ❌ Commented-out DCATDE-AP extension
- ❌ Commented-out Showcase extension
- ❌ Multiple redundant `pip3 install` commands
- ❌ Inconsistent formatting

## Best Practices

1. **One package per line** - Easier to read and track changes
2. **Clear comments** - Group extensions by functionality
3. **Consistent formatting** - Use backslash continuation for multi-line commands
4. **Version control** - Always specify versions for production
5. **Layer optimization** - Group related operations to minimize Docker layers
