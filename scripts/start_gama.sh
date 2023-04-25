#!/bin/bash
GAMA_WORKSPACE=$1
echo "GAMA_WORKSPACE: $GAMA_WORKSPACE"
port=${2:-6868}
docker run --name gama-server --rm -it -p ${port}:${port} -v ${GAMA_WORKSPACE}:/TouristFlow gamaplatform/gama:1.9.0 -socket $port