#!/bin/bash
/usr/bin/docker run --rm -p 4312:8000 -v /storage/store/TADMaster:/var/www/html/TADMaster/Site/storage -it -d --name TADMaster tadmasterserver
