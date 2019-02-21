include shared-make-configuration.cfg

WERROR_FLAGS= -Wall -Werror=implicit-function-declaration -Werror=return-type -Werror=unused-but-set-variable -Werror=unused-variable -Werror=strict-aliasing=3

XML_INCLUDE_DIR=/usr/local/Cellar/libxml2/2.9.9_2/include/libxml2
XML_LIB_DIR=/usr/local/Cellar/libxml2/2.9.9_2/lib
OPENSSL_INCLUDE_DIR=/usr/local/Cellar/openssl/1.0.2q/include/ 
OPENSSL_LIB_DIR=/usr/local/Cellar/openssl/1.0.2q/lib/

CFLAGS = -g -Wall -Wimplicit-function-declaration -MMD
CFLAGS += -I $(XML_INCLUDE_DIR) -I $(OPENSSL_INCLUDE_DIR)

LDFLAGS = -L $(XML_LIB_DIR) -L $(OPENSSL_LIB_DIR)
LIBS = -l xml2 -l crypto -l dl -l pthread -l c

SRC = $(wildcard *.c)

MAINS=$(filter %_main.c,$(SRC))
NON_MAINS = $(filter-out $(MAINS),$(wildcard *.c))
OBJ = $(NON_MAINS:.c=.o)
EXECUTABLES=$(MAINS:_main.c=.out)



execs:$(EXECUTABLES)

vars:
	@echo "NON_MAINS = $(NON_MAINS)"
	@echo "MAINS = $(MAINS)"
	@echo "OBJ = $(OBJ)"

%.o:$.c
	$(CC) $< $(CFLAGS) -c -o $@

%.out:%_main.o $(OBJ)
	$(CC) $(LDFLAGS) $< $(OBJ) $(LIBS) -o $@

clean:
	rm -f *.o; rm -f $(EXECUTABLES); rm -rf $(SWDEST) .fo ; rm -rf *.d

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
