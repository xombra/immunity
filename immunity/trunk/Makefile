help:
	@echo "Please run 'sudo make install' to install immunity."

installfiles:
	mkdir -p $(DESTDIR)/usr/ $(DESTDIR)/var/lib/immunity
	cp -r bin share $(DESTDIR)/usr/
	cp -r etc $(DESTDIR)/

install: installfiles
	addgroup --system immunity
