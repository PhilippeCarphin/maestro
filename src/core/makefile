include shared-make-configuration.cfg

WERROR_FLAGS= -Wall -Werror=implicit-function-declaration -Werror=return-type -Werror=unused-but-set-variable -Werror=unused-variable -Werror=strict-aliasing=3

CFLAGS = -g -Wall -Wimplicit-function-declaration
LIB=-lc -lcrypto -lz -ldl ${XC40_DYNAMIC_FLAG}

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

BINDIR=bin
INCDIR=include
LIBDIR=lib
WRAPDIR=src/core/wrappers
XML_INCLUDE_DIR=/usr/include/libxml2
XML_LIB_DIR=/usr/lib
CFLAGS += -I /usr/local/Cellar/include -I/usr/local/Cellar/openssl/1.0.2q/include/
LIB += -L /usr/local/Cellar/openssl/1.0.2q/lib/
#

all: prep 
	$(MAKE) prep $(EXECUTABLES)

clean:
	find . -name "*\.o" -exec rm {} \;
	rm -f $(EXECUTABLES)
	rm -rf $(BUILD_PLATFORM_FOLDER) .fo

prep:
	mkdir -p $(LIBDIR) $(INCDIR) $(BINDIR)

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
	$(CC) -g $(WERROR_FLAGS) -I $(INCDIR) $(CFLAGS) -I $(XML_INCLUDE_DIR) -c $<

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
	$(CC) $(CFLAGS) -c l2d2_Util.c
 
l2d2_commun.o: l2d2_commun.c l2d2_commun.h
	$(CC) $(CFLAGS) -c l2d2_commun.c
 
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
	$(CC) -g $(CFLAGS) $^ -L$(XML_LIB_DIR) -lxml2 $(LIB) -o tictac
	cp tictac $(BINDIR)

NODELOGGER_OBJECTS = nodelogger.o SeqUtil.o l2d2_commun.o SeqUtilServer.o \
	l2d2_socket.o QueryServer.o tictac.o nodeinfo.o SeqNode.o SeqLoopsUtil.o \
	XmlUtils.o SeqNameValues.o SeqListNode.o SeqDatesUtil.o getopt_long.o \
	FlowVisitor.o ResourceVisitor.o SeqDepends.o

nodelogger: nodelogger_main.c $(NODELOGGER_OBJECTS)
	$(CC) -g $^ -I $(CFLAGS) -I $(XML_INCLUDE_DIR) -L$(XML_LIB_DIR) -lxml2 $(LIB) -I$(INCDIR) -o nodelogger
	cp nodelogger $(BINDIR)

LOGREADER_OBJECTS = logreader.o SeqUtil.o SeqDatesUtil.o l2d2_commun.o         \
	SeqListNode.o getopt_long.o

logreader: logreader_main.c $(LOGREADER_OBJECTS)
	$(CC) -g $^ $(CFLAGS) $(LIB) -o $@
	cp logreader $(BINDIR)

MAESTRO_OBJECTS = maestro.o logreader.o nodelogger.o tictac.o nodeinfo.o \
	SeqNode.o SeqLoopsUtil.o XmlUtils.o SeqNameValues.o SeqListNode.o SeqDatesUtil.o \
	SeqUtil.o l2d2_commun.o SeqUtilServer.o QueryServer.o l2d2_socket.o \
	runcontrollib.o ocmjinfo.o expcatchup.o getopt_long.o ResourceVisitor.o \
	FlowVisitor.o SeqDepends.o

maestro: maestro_main.c $(MAESTRO_OBJECTS)
	$(CC) -g $^ $(CFLAGS) -I $(INCDIR) -L $(XML_LIB_DIR) -lxml2 $(LIB) -o maestro; \
	cp maestro $(BINDIR);

EXPCATCHUP_OBJECTS = expcatchup.o getopt_long.o SeqUtil.o XmlUtils.o           \
	SeqListNode.o l2d2_commun.o

expcatchup:expcatchup_main.c $(EXPCATCHUP_OBJECTS)
	$(CC) -g $^ $(CFLAGS) -L $(XML_LIB_DIR) -lxml2 $(LIB) -o $@; \
	cp expcatchup $(BINDIR);

NODEINFO_OBJECTS = SeqUtil.o SeqNode.o XmlUtils.o SeqLoopsUtil.o l2d2_commun.o \
	QueryServer.o l2d2_socket.o SeqListNode.o SeqDatesUtil.o SeqUtilServer.o \
	tictac.o SeqNameValues.o nodeinfo.o getopt_long.o FlowVisitor.o \
	ResourceVisitor.o SeqDepends.o

nodeinfo: nodeinfo_main.c $(NODEINFO_OBJECTS)
	$(CC) -g $^ $(CFLAGS) -I $(XML_INCLUDE_DIR) -L $(XML_LIB_DIR) -lxml2 $(LIB) -o $@;\
	cp nodeinfo $(BINDIR)

getdef:	getdef_main.o SeqUtil.o SeqListNode.o l2d2_commun.o getopt_long.o
	$(CC) -g -c getdef_main.c $(CFLAGS)
	$(CC) -g getdef_main.o SeqUtil.o SeqListNode.o l2d2_commun.o getopt_long.o $(LIB) -o getdef
	cp getdef $(BINDIR)

mserver: $(L2D2SOBJECTS)
	$(CC) $(L2D2SOBJECTS) $(LIB) $(LIBTH) $(CFLAGS) -o mserver; \
	cp mserver $(BINDIR);

madmin: $(L2D2AOBJECTS)
	$(CC) $(L2D2AOBJECTS) $(LIB) $(LIBTH) $(CFLAGS) -o madmin; \
	cp madmin $(BINDIR);

TSVINFO_OBJECTS = tsvinfo.o SeqNodeCensus.o nodeinfo.o SeqUtil.o \
	SeqNode.o SeqNameValues.o SeqLoopsUtil.o SeqListNode.o FlowVisitor.o   \
	ResourceVisitor.o XmlUtils.o SeqDatesUtil.o tictac.o l2d2_commun.o     \
	QueryServer.o l2d2_socket.o SeqUtilServer.o getopt_long.o SeqDepends.o

tsvinfo: tsvinfo_main.c $(TSVINFO_OBJECTS)
	$(CC) $^ -g $(CFLAGS) $(WERROR_FLAGS) $(CFLAGS) -L $(XML_LIB_DIR) -lxml2 $(LIB) -o $@
	cp $@ $(BINDIR);

TEST_OBJECTS = SeqUtil.o SeqNode.o XmlUtils.o SeqLoopsUtil.o l2d2_commun.o \
	QueryServer.o l2d2_socket.o SeqListNode.o SeqDatesUtil.o SeqUtilServer.o \
	tictac.o SeqNameValues.o nodeinfo.o getopt_long.o FlowVisitor.o \
	ResourceVisitor.o SeqDepends.o tsvinfo.o SeqNodeCensus.o

mtest:	mtest_main.c $(TEST_OBJECTS)
	$(CC) $^ -g $(CFLAGS) $(WERROR_FLAGS) -I $(XML_INCLUDE_DIR) -L $(XML_LIB_DIR) -lxml2 $(LIB) -o $@
	cp $@ $(BINDIR)

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

