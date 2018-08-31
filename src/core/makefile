
include ../config.mk

MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:
.SUFFIXES: .c .o

WERROR_FLAGS= -Wall -Werror=implicit-function-declaration -Werror=return-type -Werror=unused-but-set-variable -Werror=unused-variable -Werror=strict-aliasing=3
CFLAGS = -Wall -Wimplicit-function-declaration -Wl,--allow-multiple-definition 
LIB=-lc -lcrypto -lz -ldl
LIBTH=-lpthread
CFLAGS1 = 
CFLAGS2 = -lefence -I../inc -DREENTRANT -Wall -Wextra -Wno-unused -D__DEBUG -DIGNORE_EMPTY_TEXT_NODES
ROXML_OBJECTS = l2d2_roxml.o l2d2_roxml-internal.o l2d2_roxml-parse-engine.o
L2D2SOBJECTS  = l2d2_server.o l2d2_socket.o l2d2_Util.o l2d2_commun.o l2d2_lists.o $(ROXML_OBJECTS) SeqUtil.o SeqLoopsUtil.o SeqNameValues.o SeqNode.o SeqListNode.o SeqDepends.o
L2D2AOBJECTS  = l2d2_admin.o l2d2_socket.o l2d2_Util.o l2d2_commun.o l2d2_lists.o $(ROXML_OBJECTS)  SeqUtil.o SeqLoopsUtil.o SeqNameValues.o SeqNode.o SeqListNode.o SeqDepends.o
OBJECTS=SeqUtil.o SeqNode.o SeqListNode.o SeqNameValues.o SeqLoopsUtil.o SeqDatesUtil.o \
runcontrollib.o nodelogger.o maestro.o nodeinfo.o tictac.o expcatchup.o XmlUtils.o \
QueryServer.o SeqUtilServer.o l2d2_socket.o l2d2_commun.o ocmjinfo.o logreader.o $(ROXML_OBJECTS)
EXECUTABLES=nodelogger maestro nodeinfo tictac expcatchup getdef logreader mserver madmin tsvinfo mtest

#

all: prep 
	$(MAKE) prep $(EXECUTABLES) wrapper

wrapper: 
	rm -rf $(BINDIR)/wrappers
	mkdir -p $(BINDIR)/wrappers
	cd wrappers; for file in *; do \
	    cp $${file} $(BINDIR)/wrappers/maestro_${VERSION}.$${file}; \
	done; \
	cd ..

clean:
	rm -f *.o; rm -f $(EXECUTABLES); rm -rf $(SWDEST) .fo

prep:
	if [ ! -d $(SWDEST) ] ; then \
	   echo "Creating $(SWDEST)" ; \
	   mkdir -p $(SWDEST); mkdir $(SWDEST)/include; mkdir $(SWDEST)/bin; \
	fi; \

#objects

objects:	$(OBJECTS)

runcontrollib.o:	runcontrollib.c runcontrollib.h nodelogger.h nodeinfo.h
	$(CC) $(CFLAGS) -c runcontrollib.c

SeqNode.o:	SeqNode.c SeqNode.h
	$(CC) $(CFLAGS) -c SeqNode.c;

SeqListNode.o:	SeqListNode.c
	$(CC) $(CFLAGS) -c SeqListNode.c

SeqNameValues.o:	SeqNameValues.c
	$(CC) $(CFLAGS) -c SeqNameValues.c

SeqLoopsUtil.o:	SeqLoopsUtil.c
	$(CC) $(CFLAGS) -c SeqLoopsUtil.c

SeqDatesUtil.o:	SeqDatesUtil.c
	$(CC) $(CFLAGS) -c  SeqDatesUtil.c

XmlUtils.o:	XmlUtils.c
	$(CC) $(CFLAGS) -I $(INCDIR) -I $(XML_INCLUDE_DIR) -c XmlUtils.c

SeqUtil.o:	SeqUtil.c SeqUtil.h
	$(CC) $(CFLAGS) -Wall -c SeqUtil.c

SeqUtilServer.o: SeqUtilServer.c QueryServer.h
	$(CC) $(CFLAGS) -c SeqUtilServer.c
 
QueryServer.o: QueryServer.c QueryServer.h
	$(CC) $(CFLAGS) -c QueryServer.c
  
l2d2_socket.o: l2d2_socket.h l2d2_socket.c 
	$(CC) $(CFLAGS) -c l2d2_socket.c

expcatchup.o:	expcatchup.c expcatchup.h
	$(CC) $(CFLAGS) -I $(INCDIR) -I $(XML_INCLUDE_DIR) -c expcatchup.c

FlowVisitor.o:  FlowVisitor.c FlowVisitor.h nodeinfo.c nodeinfo.h ResourceVisitor.h ResourceVisitor.c
	$(CC) -c $< $(CFLAGS) -I $(INCDIR) -I $(XML_INCLUDE_DIR)

SeqDepends.o: SeqDepends.c SeqDepends.h
	$(CC) -I $(INCDIR) -I $(XML_INCLUDE_DIR) -c $<

ResourceVisitor.o: ResourceVisitor.c ResourceVisitor.h nodeinfo.c nodeinfo.h
	$(CC) -c $< $(CFLAGS) -I $(INCDIR) -I $(XML_INCLUDE_DIR)

SeqNodeCensus.o: SeqNodeCensus.c SeqNodeCensus.h FlowVisitor.h
	$(CC) -c $< $(CFLAGS) -I $(INCDIR) -I $(XML_INCLUDE_DIR)

tsvinfo.o: tsvinfo.c tsvinfo.h nodeinfo.o
	$(CC) -c $< $(CFLAGS) -I $(INCDIR) -I $(XML_INCLUDE_DIR)

nodeinfo.o:	nodeinfo.c nodeinfo.h FlowVisitor.h runcontrollib.h ResourceVisitor.c ResourceVisitor.h
	$(CC) $(CFLAGS) -I $(INCDIR) -I $(XML_INCLUDE_DIR) -c $<

logreader.o:	logreader.c logreader.h logreader_main.c
	$(CC) $(CFLAGS) -c logreader.c

maestro.o:	maestro.c QueryServer.h maestro.h nodeinfo.h runcontrollib.h nodelogger.h tictac.h SeqUtil.h
	$(CC) $(CFLAGS) -c maestro.c -I $(XML_INCLUDE_DIR)

ocmjinfo.o:	ocmjinfo.c ocmjinfo.h 
	$(CC) $(CFLAGS) -c ocmjinfo.c

l2d2_lists.o: l2d2_lists.h l2d2_lists.c
	$(CC) -c l2d2_lists.c

l2d2_Util.o: l2d2_Util.c l2d2_Util.h
	$(CC) -c l2d2_Util.c
 
l2d2_commun.o: l2d2_commun.c l2d2_commun.h
	$(CC) -c l2d2_commun.c
 
l2d2_admin.o: l2d2_admin.c
	$(CC) -c l2d2_admin.c
 
l2d2_server.o: l2d2_server.c l2d2_server.h
	$(CC) -c l2d2_server.c
 
l2d2_roxml.o: l2d2_roxml.c
	$(CC)  $(CFLAGS2) -c l2d2_roxml.c
 
l2d2_roxml-internal.o: l2d2_roxml-internal.c
	$(CC)  $(CFLAGS2) -c l2d2_roxml-internal.c
 
l2d2_roxml-parse-engine.o: l2d2_roxml-parse-engine.c
	$(CC)  $(CFLAGS2) -c l2d2_roxml-parse-engine.c
 
nodelogger.o:	nodelogger.c nodelogger.h SeqUtil.c l2d2_commun.c l2d2_Util.c l2d2_socket.c
	$(CC) $(CFLAGS) -c nodelogger.c 

tictac.o:	tictac.c tictac.h
	$(CC) $(CFLAGS) -c tictac.c

getopt_long.o:	getopt_long.c getopt.h
	$(CC) -c getopt_long.c

# Targets for command line executables:
#
# For reference (I always forget them):
# $^ is the whole prerequisite list
# $@ is the target name
# $< the name of the first prerequisite

TICTAC_OBJECTS = tictac.o SeqUtil.o QueryServer.o l2d2_socket.o SeqUtilServer.o \
	l2d2_commun.o SeqListNode.o getopt_long.o

tictac:	tictac_main.c $(TICTAC_OBJECTS)
	$(CC) $^ -L$(XML_LIB_DIR) -lxml2 $(LIB) -o tictac
	mv tictac $(BINDIR)

NODELOGGER_OBJECTS = nodelogger.o SeqUtil.o l2d2_commun.o SeqUtilServer.o \
	l2d2_socket.o QueryServer.o tictac.o nodeinfo.o SeqNode.o SeqLoopsUtil.o \
	XmlUtils.o SeqNameValues.o SeqListNode.o SeqDatesUtil.o getopt_long.o \
	FlowVisitor.o ResourceVisitor.o SeqDepends.o

nodelogger: nodelogger_main.c $(NODELOGGER_OBJECTS)
	$(CC) $^ -I $(XML_INCLUDE_DIR) -L$(XML_LIB_DIR) -lxml2 $(LIB) -I$(INCDIR) -o nodelogger
	mv nodelogger $(BINDIR)

LOGREADER_OBJECTS = logreader.o SeqUtil.o SeqDatesUtil.o l2d2_commun.o         \
	SeqListNode.o getopt_long.o

logreader: logreader_main.c $(LOGREADER_OBJECTS)
	$(CC) $^ $(LIB) -o $@
	mv logreader $(BINDIR)

MAESTRO_OBJECTS = maestro.o logreader.o nodelogger.o tictac.o nodeinfo.o \
	SeqNode.o SeqLoopsUtil.o XmlUtils.o SeqNameValues.o SeqListNode.o SeqDatesUtil.o \
	SeqUtil.o l2d2_commun.o SeqUtilServer.o QueryServer.o l2d2_socket.o \
	runcontrollib.o ocmjinfo.o expcatchup.o getopt_long.o ResourceVisitor.o \
	FlowVisitor.o SeqDepends.o

maestro: maestro_main.c $(MAESTRO_OBJECTS)
	$(CC) $^ -I $(INCDIR) -L $(XML_LIB_DIR) -lxml2 $(LIB) -o maestro; \
	mv maestro $(BINDIR);

EXPCATCHUP_OBJECTS = expcatchup.o getopt_long.o SeqUtil.o XmlUtils.o           \
	SeqListNode.o l2d2_commun.o

expcatchup:expcatchup_main.c $(EXPCATCHUP_OBJECTS)
	$(CC) $^ -L $(XML_LIB_DIR) -lxml2 $(LIB) -o $@; \
	mv expcatchup $(BINDIR);

NODEINFO_OBJECTS = SeqUtil.o SeqNode.o XmlUtils.o SeqLoopsUtil.o l2d2_commun.o \
	QueryServer.o l2d2_socket.o SeqListNode.o SeqDatesUtil.o SeqUtilServer.o \
	tictac.o SeqNameValues.o nodeinfo.o getopt_long.o FlowVisitor.o \
	ResourceVisitor.o SeqDepends.o

nodeinfo: nodeinfo_main.c $(NODEINFO_OBJECTS)
	$(CC) $^ -I $(XML_INCLUDE_DIR) -L $(XML_LIB_DIR) -lxml2 $(LIB) -o $@;\
	mv nodeinfo $(BINDIR)

getdef:	getdef_main.o SeqUtil.o SeqListNode.o l2d2_commun.o getopt_long.o
	$(CC) -c getdef_main.c 
	$(CC) getdef_main.o SeqUtil.o SeqListNode.o l2d2_commun.o getopt_long.o $(LIB) -o getdef
	mv getdef $(BINDIR)

mserver: $(L2D2SOBJECTS)
	$(CC) $(CFLAGS) $(L2D2SOBJECTS) $(LIB) $(LIBTH) -o mserver; \
	mv mserver $(BINDIR);

madmin: $(L2D2AOBJECTS)
	$(CC) $(CFLAGS) $(L2D2AOBJECTS) $(LIB) $(LIBTH) -o madmin; \
	mv madmin $(BINDIR);

TSVINFO_OBJECTS = tsvinfo.o SeqNodeCensus.o nodeinfo.o SeqUtil.o \
	SeqNode.o SeqNameValues.o SeqLoopsUtil.o SeqListNode.o FlowVisitor.o   \
	ResourceVisitor.o XmlUtils.o SeqDatesUtil.o tictac.o l2d2_commun.o     \
	QueryServer.o l2d2_socket.o SeqUtilServer.o getopt_long.o SeqDepends.o

tsvinfo: tsvinfo_main.c $(TSVINFO_OBJECTS)
	$(CC) $^ -L $(XML_LIB_DIR) -lxml2 $(LIB) -o $@
	mv $@ $(BINDIR);

TEST_OBJECTS = SeqUtil.o SeqNode.o XmlUtils.o SeqLoopsUtil.o l2d2_commun.o \
	QueryServer.o l2d2_socket.o SeqListNode.o SeqDatesUtil.o SeqUtilServer.o \
	tictac.o SeqNameValues.o nodeinfo.o getopt_long.o FlowVisitor.o \
	ResourceVisitor.o SeqDepends.o tsvinfo.o SeqNodeCensus.o

mtest:	mtest_main.c $(TEST_OBJECTS)
	$(CC) $^ -I $(XML_INCLUDE_DIR) -L $(XML_LIB_DIR) -lxml2 $(LIB) -o $@
	mv $@ $(BINDIR)

