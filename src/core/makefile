include shared-make-configuration.cfg

WERROR_FLAGS= -Wall -Werror=implicit-function-declaration -Werror=return-type -Werror=unused-but-set-variable -Werror=unused-variable -Werror=strict-aliasing=3

CFLAGS = -g -Wall -Wimplicit-function-declaration -MMD

LIB=-lc -lcrypto -lz -ldl
LIBTH=-lpthread

MAINS=$(wildcard *_main.c)
EXECUTABLES=$(MAINS:_main.c=.out)

execs:$(EXECUTABLES)

all: prep 
	$(MAKE) prep $(EXECUTABLES)

clean:
	rm -f *.o; rm -f $(EXECUTABLES); rm -rf $(SWDEST) .fo ; rm -rf *.d

prep:
	mkdir -p $(LIBDIR) $(INCDIR) $(BINDIR)

%.o:%.c
	$(CC) $< $(CFLAGS) -c -o $@

%.out:%_main.o
	$(CC) -g $^ -L $(XML_LIB_DIR) -lxml2 $(LIB) -o $@

OBJECTS=SeqUtil.o SeqNode.o SeqListNode.o SeqNameValues.o SeqLoopsUtil.o SeqDatesUtil.o \
runcontrollib.o nodelogger.o maestro.o nodeinfo.o tictac.o expcatchup.o XmlUtils.o \
QueryServer.o SeqUtilServer.o l2d2_socket.o l2d2_commun.o ocmjinfo.o logreader.o $(ROXML_OBJECTS)

ROXML_OBJECTS = l2d2_roxml.o l2d2_roxml-internal.o l2d2_roxml-parse-engine.o

%.o:%.c
	$(CC) $< $(CFLAGS) -c -o $@

L2D2SOBJECTS  = l2d2_server.o l2d2_socket.o l2d2_Util.o l2d2_commun.o l2d2_lists.o $(ROXML_OBJECTS) SeqUtil.o SeqLoopsUtil.o SeqNameValues.o SeqNode.o SeqListNode.o SeqDepends.o

L2D2AOBJECTS  = l2d2_admin.o l2d2_socket.o l2d2_Util.o l2d2_commun.o l2d2_lists.o $(ROXML_OBJECTS)  SeqUtil.o SeqLoopsUtil.o SeqNameValues.o SeqNode.o SeqListNode.o SeqDepends.o

TICTAC_OBJECTS = tictac.o SeqUtil.o QueryServer.o l2d2_socket.o SeqUtilServer.o \
	l2d2_commun.o SeqListNode.o getopt_long.o
tictac.out:	$(TICTAC_OBJECTS)

NODELOGGER_OBJECTS = nodelogger.o SeqUtil.o l2d2_commun.o SeqUtilServer.o \
	l2d2_socket.o QueryServer.o tictac.o nodeinfo.o SeqNode.o SeqLoopsUtil.o \
	XmlUtils.o SeqNameValues.o SeqListNode.o SeqDatesUtil.o getopt_long.o \
	FlowVisitor.o ResourceVisitor.o SeqDepends.o
nodelogger.out: nodelogger_main.o $(NODELOGGER_OBJECTS)

LOGREADER_OBJECTS = logreader.o SeqUtil.o SeqDatesUtil.o l2d2_commun.o         \
	SeqListNode.o getopt_long.o
logreader.out:$(LOGREADER_OBJECTS)

MAESTRO_OBJECTS = maestro.o logreader.o nodelogger.o tictac.o nodeinfo.o \
	SeqNode.o SeqLoopsUtil.o XmlUtils.o SeqNameValues.o SeqListNode.o SeqDatesUtil.o \
	SeqUtil.o l2d2_commun.o SeqUtilServer.o QueryServer.o l2d2_socket.o \
	runcontrollib.o ocmjinfo.o expcatchup.o getopt_long.o ResourceVisitor.o \
	FlowVisitor.o SeqDepends.o
maestro.out: $(MAESTRO_OBJECTS)



EXPCATCHUP_OBJECTS = expcatchup.o getopt_long.o SeqUtil.o XmlUtils.o           \
	SeqListNode.o l2d2_commun.o

expcatchup.out: $(EXPCATCHUP_OBJECTS)

NODEINFO_OBJECTS = SeqUtil.o SeqNode.o XmlUtils.o SeqLoopsUtil.o l2d2_commun.o \
	QueryServer.o l2d2_socket.o SeqListNode.o SeqDatesUtil.o SeqUtilServer.o \
	tictac.o SeqNameValues.o nodeinfo.o getopt_long.o FlowVisitor.o \
	ResourceVisitor.o SeqDepends.o

nodeinfo.out:$(NODEINFO_OBJECTS)

getdef.out:	getdef_main.o SeqUtil.o SeqListNode.o l2d2_commun.o getopt_long.o

mserver.out: $(L2D2SOBJECTS)

madmin.out: $(L2D2AOBJECTS)

TSVINFO_OBJECTS = tsvinfo.o SeqNodeCensus.o nodeinfo.o SeqUtil.o \
	SeqNode.o SeqNameValues.o SeqLoopsUtil.o SeqListNode.o FlowVisitor.o   \
	ResourceVisitor.o XmlUtils.o SeqDatesUtil.o tictac.o l2d2_commun.o     \
	QueryServer.o l2d2_socket.o SeqUtilServer.o getopt_long.o SeqDepends.o

tsvinfo.out:$(TSVINFO_OBJECTS)

TEST_OBJECTS = SeqUtil.o SeqNode.o XmlUtils.o SeqLoopsUtil.o l2d2_commun.o \
	QueryServer.o l2d2_socket.o SeqListNode.o SeqDatesUtil.o SeqUtilServer.o \
	tictac.o SeqNameValues.o nodeinfo.o getopt_long.o FlowVisitor.o \
	ResourceVisitor.o SeqDepends.o tsvinfo.o SeqNodeCensus.o

mtest.out:$(TEST_OBJECTS)


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

-include *.d

# Compilation sur mac PHIL
CFLAGS += -I /usr/local/Cellar/include -I/usr/local/Cellar/openssl/1.0.2q/include/ -I $(XML_INCLUDE_DIR)
LIB += -L /usr/local/Cellar/openssl/1.0.2q/lib/
