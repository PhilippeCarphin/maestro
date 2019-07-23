#!/bin/bash

# Prints 'true' if this environment has internet access, 'false' otherwise.

echo -e "GET http://google.com HTTP/1.0\n\n" | nc -w 1 google.com 80 > /dev/null
if [ $? -eq 0 ]; then
    echo "true"
else
    echo "false"
fi
