include shared-make-configuration.cfg

XML_LIB_DIR=/usr/lib
XML_INCLUDE_DIR=/usr/include/libxml2

BINDIR?=bin
INCDIR=include

WERROR_FLAGS=-Werror=implicit-function-declaration -Werror=return-type
WERROR_1337_FLAGS= -Werror=unused-but-set-variable -Werror=unused-variable -Werror=strict-aliasing=3

CFLAGS = -Wall $(WERROR_FLAGS) -I../inc -DREENTRANT -D__DEBUG -DIGNORE_EMPTY_TEXT_NODES -I$(XML_INCLUDE_DIR) -I$(INCDIR) -MMD
ARFLAGS = -crs

LD_LIBS= -lc -lz -ldl ${XC_DYNAMIC_FLAG} -lpthread -lxml2 -lcrypto 
LD_FLAGS=-L. -L$(XML_LIB_DIR)

# Source file lists
SRC = $(wildcard *.c)
MAIN_SRC = $(filter %_main.c,$(SRC))
LIB_SRC = $(filter-out $(MAIN_SRC),$(SRC))

# Targets
OBJ = $(SRC:.c=.o)
LIB_OBJ = $(LIB_SRC:.c=.o)
EXECUTABLES = $(MAIN_SRC:.c=.out)

# UNUSED VARIABLES, I don't know what they are for so I will leave them
LIBDIR=lib
WRAPDIR=src/core/wrappers

all: $(EXECUTABLES)
	rm -f ${BINDIR}/madmin
	ln -s l2d2_admin ${BINDIR}/madmin
	rm -f ${BINDIR}/mserver
	ln -s l2d2_server ${BINDIR}/mserver

# To avoid automatic deletion of .o files.  Make has implicit rules and
# if a file is not explicitely as a dependency of something else, it will
# be deleted automatically.  This rule names all *.o files explicitely as
# a dependency of the target 'objects'.
objects: $(OBJ)

%.o:%.c
	$(CC) $(CFLAGS) -c $<

%.out:%.o $(LIB_OBJ)
	$(CC) $^ $(LD_FLAGS) $(LD_LIBS) -o $@
	cp $@ $(BINDIR)/$(@:_main.out=)

clean:
	rm -f *.o *.out *.a *.d
	rm -rf $(BUILD_PLATFORM_FOLDER) .fo
	rm -f $(BINDIR)/*
	rm -f $(LIBDIR)/*

vars:
	@echo "SRC = $(SRC)"
	@echo "MAIN_SRC = $(MAIN_SRC)"
	@echo "LIB_SRC = $(LIB_SRC)"
	@echo "LIB_OBJ = $(LIB_OBJ)"
	@echo "EXECUTABLES = $(EXECUTABLES)"
	@echo "SRC = $(SRC)"

-include *.d
