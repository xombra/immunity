PYTHON ?= python

ifdef DESTDIR
INSTALL_OPTS := --root=$(DESTDIR)
endif

buildpython:
	$(PYTHON) setup.py build
	@echo "Please run 'sudo make install' now."

installpython: buildpython
	$(PYTHON) setup.py install $(INSTALL_OPTS)

installfiles:
	mkdir -p $(DESTDIR)/usr/ $(DESTDIR)/var/lib/immunity
	cp -r bin share $(DESTDIR)/usr/
	cp -r etc $(DESTDIR)/

install: installpython installfiles
	addgroup --system immunity

clean:
	$(RM) -r build
