BASEURL = http://www.mdic.gov.br/balanca/bd
FIRST := $$(date --date='-3 year' +%Y)
LAST := $$(date --date='-1 year' +%Y)
YEARS := $(shell seq ${FIRST} ${LAST})
IMPORTS := $(addprefix IMP_,$(addsuffix .csv,${YEARS}))
EXPORTS := $(addprefix EXP_,$(addsuffix .csv,${YEARS}))
.PHONY: all ${IMPORTS} ${EXPORTS}
all: ${IMPORTS} ${EXPORTS} TABELAS_AUXILIARES.xlsx
	echo "$@ success"
${IMPORTS}: IMP_%.csv:
	wget -P /code/data -Nc "$(BASEURL)/comexstat-bd/ncm/$@"
${EXPORTS}: EXP_%.csv:
	wget -P /code/data -Nc "$(BASEURL)/comexstat-bd/ncm/$@"
TABELAS_AUXILIARES.xlsx:
	wget -P /code/data -Nc $(BASEURL)/tabelas/TABELAS_AUXILIARES.xlsx
