# Compiler settings
CC = gcc

 
NUM_PRIMES = 74
CFLAGS = -Wall -Wextra -fPIC -DNUM_PRIMES=$(NUM_PRIMES) -I. -I./csifish

LDFLAGS = -shared 
 
LIBS_PATH = -L.  
 
LIBS = -lhighctidh_512

# Source files
SOURCES = helper.c points.c elliptic_curve.c action.c  csi-fish/reduce.c csi-fish/classgroup.c csi-fish/constants.c 
 
# Object files
OBJECTS = $(SOURCES:.c=.o)

# Header files
HEADERS = helper.h points.h elliptic_curve.h action.h externalfun.h models.h csi-fish/reduce.h csi-fish/classgroup.h csi-fish/parameters.h csi-fish/params.h csi-fish/constants.h  csi-fish/pool.c csi-fish/HKZbasis.c csi-fish/BKZ50.c csi-fish/BKZ40.c
 

# Output library
LIBRARY = libstreamlining.so

# Default target
all: $(LIBRARY)

$(LIBRARY): $(OBJECTS)
	$(CC) $(LDFLAGS) $(LIBS_PATH) -o $@ $^ $(LIBS) -Wl,-rpath,. -fPIC -lgmp -lcrypto

# To obtain object files
%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

# Clean
clean:
	rm -f $(OBJECTS) $(LIBRARY)

# Phony targets
.PHONY: all clean
