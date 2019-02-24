
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
	$(MAKE) -C ../src
	python3 pymaestro_setup.py install --user

tpy:py
	python3 pymaestro_example.py

######################## FIN PYTHON ############################################
