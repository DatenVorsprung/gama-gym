#!/bin/bash
port=${1:-6868}
docker run --rm -it -p ${port}:${port} -v $(pwd):/gama-gym gamaplatform/gama:1.9.0 -socket $port