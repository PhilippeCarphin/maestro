#!/bin/bash

konsole --noclose -e tail -f ~/logs/mflow/$(ls ~/logs/mflow/ | sort | tail -n 1) &
