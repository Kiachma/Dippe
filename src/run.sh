#!/bin/bash
#~/Program/SparQ/sparq  --interactive --port 4443 &
docker run  -ti --net=host dwolter/sparq --interactive --port 4443
nc 127.0.0.1 4443
#python test.py