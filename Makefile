BASEURL=http://www.mdic.gov.br/balanca/bd

all: download_datasets

data/exp.zip:
	wget -nc -O $@ $(BASEURL)/comexstat-bd/ncm/EXP_COMPLETA.zip

data/imp.zip:
	wget -nc -O $@ $(BASEURL)/comexstat-bd/ncm/IMP_COMPLETA.zip

data/aux.xlsx:
	wget -nc -O $@ $(BASEURL)/tabelas/TABELAS_AUXILIARES.xlsx

download_datasets: data/exp.zip data/imp.zip data/aux.xlsx

.PHONY: clean

clean:
	rm data/*.zip data/*.xlsx