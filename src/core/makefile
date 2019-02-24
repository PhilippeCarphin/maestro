
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
# include ../config/config.mk

WERROR_FLAGS= -Wall -Werror=implicit-function-declaration -Werror=return-type -Werror=unused-but-set-variable -Werror=unused-variable -Werror=strict-aliasing=3

XML_LIB_DIR=/usr/local/Cellar/libxml2/2.9.9_2/lib
XML_INCLUDE=-I /usr/include/libxml2 -I/usr/local/Cellar/libxml2/2.9.7/include/libxml2 -I /usr/local/Cellar/libxml2/2.9.9_2/include/libxml2  
OPENSSL_INCLUDE_DIR=/usr/local/Cellar/openssl/1.0.2q/include/
OPENSSL_LIB_DIR=/usr/local/Cellar/openssl/1.0.2q/lib/

MAESTRO_LIB_DIR = .
MAESTRO_LIBS = -l maestro

CFLAGS = -g -Wall -Wimplicit-function-declaration -MMD -Werror=implicit-function-declaration
CFLAGS += $(XML_INCLUDE) -I $(OPENSSL_INCLUDE_DIR)
CFLAGS += -Wno-unused-label -Wno-pointer-sign -Wno-unused-function
CFLAGS += -O3

LDFLAGS = -L $(XML_LIB_DIR) -L $(OPENSSL_LIB_DIR) -L $(MAESTRO_LIB_DIR)
LIBS = -l xml2 -l crypto -l dl -l pthread -l c $(MAESTRO_LIBS)

SRC = $(filter-out pymaestro.c,$(wildcard *.c))
OBJ = $(ALL_SRC:.c=.o)

MAINS=$(filter %_main.c,$(SRC))
EXECUTABLES=$(MAINS:_main.c=.out)

LIB_SRC = $(filter-out $(MAINS) pymaestro.c,$(SRC))
LIB_OBJ = $(LIB_SRC:.c=.o)
lib = libmaestro.a

.PHONY: execs
execs:$(EXECUTABLES)

$(lib):$(LIB_OBJ)
	ar -crs $@ $^

vars:
	@echo "NON_MAINS = $(NON_MAINS)"
	@echo "MAINS = $(MAINS)"
	@echo "LIB_OBJ = $(LIB_OBJ)"

%.o:%.c
	$(CC) $< $(CFLAGS) -c -o $@

%.out:%_main.o $(lib)
  # Remember, it's important that the '-l xyz' from $(LIBS) come after the
  # 'bla.o' file (but only on some compilers which is tricky)
	$(CC) $(LDFLAGS) $< $(LIBS) -o $@

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
