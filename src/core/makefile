include shared-make-configuration.cfg

XML_LIB_DIR=/usr/lib
XML_INCLUDE_DIR=/usr/include/libxml2

BINDIR?=bin
INCDIR=include
LIBDIR=lib
WRAPDIR=src/core/wrappers
XML_INCLUDE_DIR=/usr/include/libxml2
XML_LIB_DIR=/usr/lib

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

-include *.d
