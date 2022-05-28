#!/bin/bash
set -e 
command -v buildah || { echo "missing buildah binary, aborting"; exit 1; }
[ -d container ] || { echo "navigate to parent directory of \"container/\" to proceed with build"; exit 1; }
buildah bud --iidfile /tmp/kete_hs21_id --tag docker.io/bina_fs22:latest --layers=true  -f container/
#buildah push $(cat /tmp/kete_hs21_id) docker://ketehs21.azurecr.io/kete_hs21
rm -f /tmp/kete_hs21_id
