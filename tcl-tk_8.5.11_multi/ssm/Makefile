SSMPACKAGE=tcl-tk_8.5.11_multi

ssm:
	echo "Creating SSM package $(SSMPACKAGE)..."
	if [ ! -d $(SSMPACKAGE) ]; then \
	   mkdir $(SSMPACKAGE); \
	fi;
	cp -r ../src $(SSMPACKAGE); 
	cp -r ../maint $(SSMPACKAGE); 
	mkdir -p $(SSMPACKAGE)/.ssm.d;
	echo "Package: $(SSMPACKAGE)" > $(SSMPACKAGE)/.ssm.d/control; \
	echo "Version: ${VERSION}" >> $(SSMPACKAGE)/.ssm.d/control; \
	echo "Platform:" >> $(SSMPACKAGE)/.ssm.d/control; \
	echo "Maintainer: $(shell whoami)" >> $(SSMPACKAGE)/.ssm.d/control; \
	echo "BuildInfo:" >> $(SSMPACKAGE)/.ssm.d/control; \
	echo "Description: maestro tcl-tk 8.5" >> $(SSMPACKAGE)/.ssm.d/control; \
	tar cvf - $(SSMPACKAGE) | gzip -> $(SSMPACKAGE).ssm

clean:
	rm -fr $(SSMPACKAGE).ssm $(SSMPACKAGE)
