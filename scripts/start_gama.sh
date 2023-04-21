#!/bin/bash
port=${1:-6868}
WORKSPACE=$(pwd)/../Gama_Workspace/TouristFlow
docker run --rm -it -p ${port}:${port} -v $WORKSPACE:/TouristFlow gamaplatform/gama:1.9.0 -socket $port