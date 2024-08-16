#!/bin/bash

# Get current date in YYYYMMDD format
current_date=$(date +%Y%m%d)

# Rename libhighctidh_512.so to include the current date
mv libstreamlining.so ./libbackup/"libstreamlining.so_${current_date}.so"

# Navigate into the high-ctidh directory
cd str-line-c-src || exit

make 

# Copy the libstreamlining.so file to the parent directory
cp libstreamlining.so ../

# clean the previous run
make clean

# Navigate back to the original directory
cd ..
