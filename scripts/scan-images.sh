#!/usr/bin/env bash
# Vulnerability report for every image used by the compose stack.
#   - Trivy (run as container) scans OS packages and language libraries
#     (Python site-packages, Java jars, Go binaries) of each image.
#   - pip-audit additionally audits the Python environment of the ckan image
#     against the PyPA advisory database.
# Reports are written to reports/security/<timestamp>/ (git-ignored).
#
# Usage: scripts/scan-images.sh [-s SEVERITIES] [-f FAIL_ON] [-a] [-p] [-c compose.yaml]
#   -s  severities to report          (default HIGH,CRITICAL)
#   -f  exit 1 if findings of these severities exist (default: never fail)
#   -a  include vulnerabilities without a fix available (default: only fixable)
#   -p  skip pip-audit
#   -c  compose file                  (default compose.yaml)
set -uo pipefail
cd "$(dirname "$0")/.."

SEVERITY=HIGH,CRITICAL; FAIL_ON=""; UNFIXED="--ignore-unfixed"; PIP=1; COMPOSE=compose.yaml
while getopts "s:f:apc:h" o; do case $o in
  s) SEVERITY=$OPTARG;; f) FAIL_ON=$OPTARG;; a) UNFIXED="";; p) PIP=0;; c) COMPOSE=$OPTARG;;
  *) sed -n '2,14p' "$0"; exit 0;; esac; done

OUT=reports/security/$(date +%Y%m%d-%H%M%S); mkdir -p "$OUT"
CACHE=${TRIVY_CACHE_DIR:-$HOME/.cache/trivy-docker}; mkdir -p "$CACHE"
mapfile -t IMAGES < <(docker compose -f "$COMPOSE" config --images | sort -u)
[ ${#IMAGES[@]} -gt 0 ] || { echo "no images found in $COMPOSE" >&2; exit 2; }

trivy() {
  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$CACHE":/root/.cache \
    -v "$PWD/$OUT":/out aquasec/trivy:latest "$@"
}

SUMMARY=$OUT/summary.md; FOUND_FAIL=0
{ echo "# Image vulnerability report $(date -Iseconds)"; echo
  echo "Severities: $SEVERITY, ${UNFIXED:+only fixable}${UNFIXED:-including unfixed}"; echo
  echo "| image | CRITICAL | HIGH | top packages |"; echo "|---|---|---|---|"; } > "$SUMMARY"

for img in "${IMAGES[@]}"; do
  name=$(echo "$img" | tr '/:' '__')
  echo "== trivy $img" >&2
  docker image inspect "$img" >/dev/null 2>&1 || docker pull -q "$img" >/dev/null 2>&1 \
    || { echo "| $img | - | - | not available locally, skipped |" >> "$SUMMARY"; continue; }
  trivy image -q --scanners vuln --severity "$SEVERITY" $UNFIXED --format json \
        -o "/out/$name.json" "$img" >/dev/null 2>&1
  python3 - "$OUT/$name.json" "$img" "${FAIL_ON:-}" >> "$SUMMARY" <<'PY' || FOUND_FAIL=1
import sys, json, collections
path, img, fail_on = sys.argv[1:4]
try: d = json.load(open(path))
except Exception: print(f"| {img} | ? | ? | scan failed |"); sys.exit(0)
c = collections.Counter(); pk = collections.Counter()
for r in d.get("Results", []):
    for v in r.get("Vulnerabilities") or []:
        c[v["Severity"]] += 1; pk[v["PkgName"]] += 1
top = ", ".join(f"{p} ({n})" for p, n in pk.most_common(3))
print(f"| {img} | {c['CRITICAL']} | {c['HIGH']} | {top} |")
if fail_on and any(c[s] for s in fail_on.split(",")): sys.exit(1)
PY
done

if [ "$PIP" = 1 ]; then
  CKAN_IMG=$(printf '%s\n' "${IMAGES[@]}" | grep -E 'ckan$|ckan:' | grep -v solr | head -1)
  if [ -n "$CKAN_IMG" ]; then
    echo "== pip-audit $CKAN_IMG" >&2
    docker run --rm --user root --entrypoint sh "$CKAN_IMG" -c \
      'python3 -m pip install -q --break-system-packages pip-audit >/dev/null 2>&1 || python3 -m pip install -q pip-audit >/dev/null 2>&1
       pip-audit --progress-spinner off --skip-editable -f json 2>/dev/null' > "$OUT/pip-audit-ckan.json"
    python3 - "$OUT/pip-audit-ckan.json" >> "$SUMMARY" <<'PY'
import sys, json
print("\n## pip-audit (ckan image Python packages)\n")
try: d = json.load(open(sys.argv[1]))
except Exception: print("pip-audit failed or produced no output"); sys.exit(0)
rows = [(x["name"], x["version"], v["id"], ",".join(v.get("fix_versions") or ["-"]))
        for x in d.get("dependencies", []) for v in x.get("vulns", [])]
if not rows: print("no known vulnerabilities")
else:
    print("| package | installed | advisory | fixed in |\n|---|---|---|---|")
    for r in rows: print("| " + " | ".join(r) + " |")
PY
  fi
fi

cat "$SUMMARY"; echo; echo "reports in $OUT"
[ -n "$FAIL_ON" ] && [ "$FOUND_FAIL" = 1 ] && { echo "findings at $FAIL_ON level" >&2; exit 1; }
exit 0
