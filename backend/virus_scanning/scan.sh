#!/bin/bash

# Update the virus database
freshclam

# Scan the file passed as an argument
clamscan --stdout --no-summary "$1"