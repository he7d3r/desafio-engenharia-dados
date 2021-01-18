BASEURL = https://balanca.economia.gov.br/balanca/bd
FIRST := $$(date --date='-3 year' +%Y)
LAST := $$(date --date='-1 year' +%Y)
YEARS := $(shell seq ${FIRST} ${LAST})
IMPORTS := $(addprefix /data/IMP_,$(addsuffix .csv,${YEARS}))
EXPORTS := $(addprefix /data/EXP_,$(addsuffix .csv,${YEARS}))
TABLES = /data/NCM.csv /data/UF.csv#/data/TABELAS_AUXILIARES.xlsx
KINDS = import export

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

.PHONY: all \
	tests \
	test-max-total-prices-yearly \
	test-max-total-prices-monthly \
	test-min-rows-state_contributions

all: ${TABLES} ${IMPORTS} ${EXPORTS} /data/trades.db tests
	echo "$@ success"

# For an approach using curl, see https://stackoverflow.com/a/32703728/2062663
# FIXME: Replace --no-check-certificate by a proper solution
${IMPORTS}: /data/IMP_%.csv:
	wget -P /data -Nc -nv --no-check-certificate "$(BASEURL)/comexstat-bd/ncm/$(subst /data/,,$@)"
${EXPORTS}: /data/EXP_%.csv:
	wget -P /data -Nc -nv --no-check-certificate "$(BASEURL)/comexstat-bd/ncm/$(subst /data/,,$@)"
${TABLES}: /data/%:
	wget -P /data -Nc -nv --no-check-certificate "$(BASEURL)/tabelas/$(subst /data/,,$@)"

# Populate the database with with the full data, by kind and by year, and also
# add some aggregated data which will be used by the app. For the most recent
# year, include more detailed data.
/data/trades.db: ${TABLES} ${IMPORTS} ${EXPORTS}
	flask database create && \
	for KIND in ${KINDS}; do \
		YEAR=${FIRST}; while [ "$$YEAR" -le ${LAST} ]; do \
			if [ "$$KIND" = "import" ]; then \
				CSV=/data/IMP_$$YEAR.csv; \
			else \
				CSV=/data/EXP_$$YEAR.csv; \
			fi; \
			flask data aggregate-by-state-and-add $$CSV /data/UF.csv \
				/data/NCM.csv --kind=$$KIND --year=$$YEAR; \
			if [ "$$YEAR" -eq ${LAST} ]; then \
				flask data aggregate-by-month-and-state-and-add $$CSV \
					 /data/UF.csv /data/NCM.csv --kind=$$KIND --year=$$YEAR; \
				flask data aggregate-state-contributions-and-add $$CSV \
					/data/UF.csv --kind=$$KIND --year=$$YEAR; \
			fi; \
			YEAR=$$((YEAR + 1)); \
		done; \
	done

tests: test-max-total-prices-yearly \
	test-max-total-prices-monthly \
	test-min-rows-state_contributions

# Ensure no group has more than 1 total price
test-max-total-prices-yearly: /data/trades.db
	@$(eval multiple_totals=$(shell sql2csv -vH --db "$$DATABASE_URL" --query="SELECT COUNT(*) FROM (SELECT kind, year, state_code, product_code FROM top_by_state_and_year GROUP BY kind, year, state_code, product_code HAVING COUNT(*) <> 1) AS s"))
	@if [ "$(multiple_totals)" -eq "0" ]; then \
		echo "OK: There is at most one total price per combination of (kind of transaction, year, state_code and product)."; \
	else \
		echo "ERROR: Some combination of (kind of transaction, year, state_code and product) has more than one total price."; \
		exit 1; \
	fi

# Ensure no group has more than 1 total price
test-max-total-prices-monthly: /data/trades.db
	@$(eval multiple_totals=$(shell sql2csv -vH --db "$$DATABASE_URL" --query="SELECT COUNT(*) FROM (SELECT kind, year, month, state_code, product_code FROM top_by_state_and_month GROUP BY kind, year, month, state_code, product_code HAVING COUNT(*) <> 1) AS s"))
	@if [ "$(multiple_totals)" -eq "0" ]; then \
		echo "OK: There is at most one total price per combination of (kind of transaction, year, month, state_code and product)."; \
	else \
		echo "ERROR: Some combination of (kind of transaction, year, month, state_code and product) has more than one total price."; \
		exit 1; \
	fi

# Ensure the number of rows is at least twice the number of Brazilian states (2*26)
test-min-rows-state_contributions: /data/trades.db
	@$(eval min_rows=52)
	@$(eval n_rows=$(shell sql2csv -vH --db "$$DATABASE_URL" --query="SELECT COUNT(*) FROM state_contributions"))
	@if [ "$(n_rows)" -ge "$(min_rows)" ]; then \
		echo "OK: There are at least $(min_rows) rows in table 'state_contributions'"; \
	else \
		echo "ERROR: The table 'state_contributions' has $(n_rows) rows but it should have at least $(min_rows)"; \
		exit 1; \
	fi
