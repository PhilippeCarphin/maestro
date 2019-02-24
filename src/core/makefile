
#  Makefile for maestro source code
#  Copyright (C) 2011-2015  Operations division of the Canadian Meteorological Centre
#                           Environment Canada
#
#  Maestro is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation,
#  version 2.1 of the License.
#
#  Maestro is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the
#  Free Software Foundation, Inc., 59 Temple Place - Suite 330,
#  Boston, MA 02111-1307, USA.

include shared-make-configuration.cfg
MAKEFILE:=$(lastword $(MAKEFILE_LIST))

# common section definition
include ../config/config.mk

MAESTRO_LIB_DIR = .
MAESTRO_LIBS = -l maestro

# Debug info in object files
CFLAGS += -g
# Maximum optimisation level
CFLAGS += -O3
# All warnings except some of the more useless ones
CFLAGS += -Wall -Wno-unused-label -Wno-pointer-sign -Wno-unused-function
# Turn these very useful warnings into errors
CFLAGS += -Werror=implicit-function-declaration
CFLAGS += -Werror=incompatible-pointer-types
# Tell the compiler to write a *.d file that know
# what *.h files a given source file depends on
CFLAGS += -MMD
# Include directories of external libraries
CFLAGS += -I $(XML_INCLUDE_DIR) -I $(OPENSSL_INCLUDE_DIR)

# Add link directories of external libraries
LDFLAGS += -L $(XML_LIB_DIR) -L $(OPENSSL_LIB_DIR)
# Link with external libraries
LIBS += -l xml2 -l crypto
# Link with other external libraries
LIBS += -l dl -l pthread
# Add link directory of maestro lib file
LDFLAGS += -L $(MAESTRO_LIB_DIR)
# Link with maestro lib
LIBS += $(MAESTRO_LIBS)

# Flags for static linking of maestro library
ARFLAGS = -crs

# Various source file lists
SRC = $(wildcard *.c)

# Files concerning the library
LIB_SRC = $(filter-out $(MAINS_SRC),$(SRC))
LIB_OBJ = $(LIB_SRC:.c=.o)
lib = libmaestro.a

# Files concerning executables
# NOTE, there is no MAINS_OBJ. They are still targeted specifically
# NOTE  but by the specificity of the rule %.out:%_main.c
MAINS_SRC = $(filter %_main.c,$(SRC))
EXECUTABLES=$(MAINS_SRC:_main.c=.out)


.PHONY: execs
execs:$(EXECUTABLES)

$(lib):$(LIB_OBJ)
	$(AR) $(ARFLAGS) $@ $^

%.o:%.c
	$(CC) $< $(CFLAGS) -c -o $@

%.out:%_main.o $(lib)
  # Remember, it's important that the '-l xyz' from $(LIBS) come after the
  # 'bla.o' file (but only on some compilers which is tricky)
	$(CC) $< $(LDFLAGS) $(LIBS) -o $@

vars:
	@echo "MAINS = $(MAINS)"
	@echo "LIB_OBJ = $(LIB_OBJ)"

clean:
	rm -f *.o; rm -f $(EXECUTABLES); rm -rf *.d

####################### FIN DU MAKEFILE STANDARD, DEBUT CHOSES SPÉCIALES #######################
#
all: prep 
	$(MAKE) prep $(EXECUTABLES)


prep:
	mkdir -p $(LIBDIR) $(INCDIR) $(BINDIR)

###################### CIBLE POUR MODULE PYTHON #################################
#

pymaestro_lib = pymaestro.so
pymaestro_src = pymaestro.c
pymaestro_ldflags = -shared
pymaestro_ldlibs =
pymaestro_cflags = $(CFLAGS) -I /usr/include/python3.5m
pymaestro_cflags += -I /usr/local/Cellar/python/3.7.2_2/Frameworks/Python.framework/Versions/3.7/include/python3.7m

py:$(pymaestro_lib)
$(pymaestro_lib):$(pymaestro_src)
	rm -rf build
	python3 pymaestro_setup.py install --user

tpy:py
	python3 pymaestro_example.py

######################## FIN PYTHON ############################################
-include *.d
