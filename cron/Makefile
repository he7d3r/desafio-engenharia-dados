BASEURL = http://www.mdic.gov.br/balanca/bd
FIRST := $$(date --date='-3 year' +%Y)
LAST := $$(date --date='-1 year' +%Y)
YEARS := $(shell seq ${FIRST} ${LAST})
IMPORTS := $(addprefix /data/IMP_,$(addsuffix .csv,${YEARS}))
EXPORTS := $(addprefix /data/EXP_,$(addsuffix .csv,${YEARS}))
TABLES = /data/NCM.csv /data/UF.csv#/data/TABELAS_AUXILIARES.xlsx

# When run from crontab inside the container, the wrong python binary,
# causing "ModuleNotFoundError: No module named 'docopt'". See:
# * https://stackoverflow.com/q/58219936/2062663
# * https://stackoverflow.com/a/22755199/2062663
# For now, workaround it by hardcoding the python path
ifneq ("$(wildcard /usr/local/bin/python3)","")
	# This works inside the container
    PYTHON = /usr/local/bin/python3
else
	# This works locally (in my conda env)
    PYTHON = python3
endif

.PHONY: all
all: ${TABLES} ${IMPORTS} ${EXPORTS} /data/trades.db
	echo "$@ success"

# For an approach using curl, see https://stackoverflow.com/a/32703728/2062663
${IMPORTS}: /data/IMP_%.csv:
	wget -P /data -Nc -nv "$(BASEURL)/comexstat-bd/ncm/$(subst /data/,,$@)"
${EXPORTS}: /data/EXP_%.csv:
	wget -P /data -Nc -nv "$(BASEURL)/comexstat-bd/ncm/$(subst /data/,,$@)"
${TABLES}: /data/%:
	wget -P /data -Nc -nv "$(BASEURL)/tabelas/$(subst /data/,,$@)"

/data/trades.db: ${TABLES} ${IMPORTS} ${EXPORTS}
	${PYTHON} scripts/createdb.py ${IMPORTS} --db=$@ --table=import && \
	${PYTHON} scripts/createdb.py ${EXPORTS} --db=$@ --table=export && \
	${PYTHON} scripts/createdb.py /data/NCM.csv --db=$@ --table=ncm --encoding=ISO-8859-1 && \
	${PYTHON} scripts/createdb.py /data/UF.csv --db=$@ --table=uf --encoding=ISO-8859-1