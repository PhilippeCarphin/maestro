# this file contains common config that is sourced by all makefiles
WHO_I_AM=$(shell whoami)
VERSION=1.5.2
SEQ_WRAPPER=maestro_$(VERSION)
MACHINE=$(shell uname -s)
HARDWARE=$(shell uname -m | tr '_' '-')
SWDEST=dist/$(ORDENV_PLAT)
LIBDIR=$(SWDEST)/lib
OPTDIR=$(SWDEST)/opt
INCDIR=$(SWDEST)/include
BINDIR=$(SWDEST)/bin
XML_INCLUDE_DIR=/usr/local/Cellar/libxml2/2.9.9_2/include/libxml2
XML_LIB_DIR=/usr/local/Cellar/libxml2/2.9.9_2/lib

# platform specific definition
ifeq ($(MACHINE),Linux)
   CC = cc
else 
   CC = cc
endif

SSMPACKAGE=maestro_$(VERSION)_$(ORDENV_PLAT)
