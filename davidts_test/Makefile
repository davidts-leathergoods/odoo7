.PHONY: server web

help:
	@# Display help
	@grep -A1 '^[a-z0-9-]*:[^=]*$$' Makefile | grep -v ^--

install-funkload:
	# install funkload
	mkdir -p tests/funkload/log ; \
	virtualenv py27 ; \
	py27/bin/pip install -i http://openerp.inouk.fr -r req.pip
        
bootstrap-db-local:
	# Drop then reinstall a fresh database on localhost
	cd tests/funkload ; \
	../../py27/bin/fl-run-test -v install.py BootstrapDB 

bootstrap-db-davidts-audaxis-com:
	# Drop then reinstall a fresh database on localhost
	cd tests/funkload ; \
	../../py27/bin/fl-run-test -v install.py BootstrapDB -u http://davidts.audaxis.com
