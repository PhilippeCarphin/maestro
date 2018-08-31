
WHO_I_AM=$(shell whoami)
VERSION=1.5.1
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

MAESTRO_PACKAGE=maestro_$(VERSION)_$(ORDENV_PLAT)
TCL_PACKAGE=tcl_$(VERSION)_$(ORDENV_PLAT)
