#!/bin/bash

# Get current date in YYYYMMDD format
current_date=$(date +%Y%m%d)

# Rename libhighctidh_512.so to include the current date
mv libhighctidh_512.so ./libbackup/"libhighctidh_512_${current_date}.so"

# Navigate into the high-ctidh directory
cd high-ctidh || exit

# Run the autogen script 
# ./autogen  # (use it one new machines)

# Run make with the specified targets
# make libhighctidh_511.so libhighctidh_512.so libhighctidh_1024.so libhighctidh_2048.so
make libhighctidh_512.so


# Copy the libhighctidh_512.so file to the parent directory
cp libhighctidh_512.so ../

# clean the previous run
make clean

# Navigate back to the original directory
cd ..

