# Run this script before running 'make' to configure the build process.
# It creates the config.mk file according to user input.

echo "Build version (example: 1.5.1):"
read VERSION

CONFIG_FILENAME="config.mk"
rm -f $CONFIG_FILENAME
echo "

WHO_I_AM=$(shell whoami)
SEQ_WRAPPER=maestro_$(VERSION)
MACHINE=$(shell uname -s)
HARDWARE=$(shell uname -m | tr '_' '-')
SWDEST=$(shell pwd)/build/$(ORDENV_PLAT)
LIBDIR=$(SWDEST)/lib
INCDIR=$(SWDEST)/include
BINDIR=$(SWDEST)/bin
XML_INCLUDE_DIR=/usr/include/libxml2
XML_LIB_DIR=/usr/lib
CC = cc
SSMPACKAGE=maestro_$(VERSION)_$(ORDENV_PLAT)

" >> $CONFIG_FILENAME
