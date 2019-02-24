include config/config.mk

all: prep wrappers
	$(MAKE) -C src execs
	@ cp -v src/*.out $(BINDIR)
	@ for f in $$(ls $(BINDIR)/*.out) ; do mv -v $${f} $${f%%.out} ; done
	@# @ for f in $$(ls $(OPTDIR)) ; do ln -sv ../opt/$${f} $(BINDIR)/$${f%%.out} ; done
	@ cp -v src/*.h $(INCDIR)
	@ cp -v src/*.a $(LIBDIR)

prep:
	mkdir -p $(SWDEST)
	mkdir -p $(SWDEST)
	mkdir -p $(OPTDIR)
	mkdir -p $(BINDIR)
	mkdir -p $(INCDIR)
	mkdir -p $(LIBDIR)

wrappers: prep
	rm -rf $(BINDIR)/wrappers
	mkdir -p $(BINDIR)/wrappers
	@ for file in $$(ls src/wrappers); do \
	    cp -v src/wrappers/$${file} $(BINDIR)/wrappers/maestro_${VERSION}.$${file}; \
	done; \

clean:
	rm -rf $(SWDEST)
	$(MAKE) -C src $@

distclean: clean
	rm -fr bin/$(BASE_ARCH) ; \
	git clean -dfX && git clean -dfx
	# find . -name "*~" -exec rm -f {} \;

install: all
	# cd ssm ; $(MAKE) $@

uninstall:
	# $(MAKE) -C ssm $@
