BASEURL = http://www.mdic.gov.br/balanca/bd
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
	test-min-rows-uf \
	test-min-rows-ncm \
	test-min-rows-import \
	test-min-rows-export \
	test-min-distinct-prod-import \
	test-min-distinct-prod-export

all: ${TABLES} ${IMPORTS} ${EXPORTS} /data/trades.db tests
	echo "$@ success"

# For an approach using curl, see https://stackoverflow.com/a/32703728/2062663
${IMPORTS}: /data/IMP_%.csv:
	wget -P /data -Nc -nv "$(BASEURL)/comexstat-bd/ncm/$(subst /data/,,$@)"
${EXPORTS}: /data/EXP_%.csv:
	wget -P /data -Nc -nv "$(BASEURL)/comexstat-bd/ncm/$(subst /data/,,$@)"
${TABLES}: /data/%:
	wget -P /data -Nc -nv "$(BASEURL)/tabelas/$(subst /data/,,$@)"

# Populate the database with with the full data, by kind and by year, and also
# add some aggregated data which will be used by the app. For the most recent
# year, include more detailed data.
/data/trades.db: ${TABLES} ${IMPORTS} ${EXPORTS}
	flask create-db && \
	${PYTHON} src/scripts/add_data.py /data/NCM.csv --db=$$DATABASE_URL \
		--table=ncm --encoding=ISO-8859-1 && \
	${PYTHON} src/scripts/add_data.py /data/UF.csv --db=$$DATABASE_URL \
		--table=uf --encoding=ISO-8859-1 && \
	for KIND in ${KINDS}; do \
		YEAR=${FIRST}; while [ "$$YEAR" -le ${LAST} ]; do \
			if [ "$$KIND" = "import" ]; then \
				${PYTHON} src/scripts/add_data.py /data/IMP_$$YEAR.csv \
					--db=$$DATABASE_URL --table=$$KIND; \
			else \
				${PYTHON} src/scripts/add_data.py /data/EXP_$$YEAR.csv \
					--db=$$DATABASE_URL --table=$$KIND; \
			fi; \
			if [ "$$YEAR" -eq ${LAST} ]; then \
				${PYTHON} src/scripts/add_aggregated_data.py --db=$$DATABASE_URL \
					--table=$$KIND --year=$$YEAR --more-data;\
			else \
				${PYTHON} src/scripts/add_aggregated_data.py --db=$$DATABASE_URL \
					--table=$$KIND --year=$$YEAR; \
			fi; \
			YEAR=$$((YEAR + 1)); \
		done; \
	done

tests: test-min-rows-uf \
	test-min-rows-ncm \
	test-min-rows-import \
	test-min-rows-export \
	test-min-distinct-prod-import \
	test-min-distinct-prod-export \
	test-max-total-prices-yearly \
	test-max-total-prices-monthly \
	test-min-rows-state_contributions

# Ensure the number of rows is at least the number of Brazilian states (26)
test-min-rows-uf: /data/trades.db
	@$(eval min_rows=26)
	@$(eval n_rows=$(shell sql2csv -vH --db "$$DATABASE_URL" --query="SELECT COUNT(*) FROM uf"))
	@if [ "$(n_rows)" -ge "$(min_rows)" ]; then \
		echo "OK: There are at least $(min_rows) rows in table 'uf'"; \
	else \
		echo "ERROR: The table 'uf' has $(n_rows) rows but it should have at least $(min_rows)"; \
		exit 1; \
	fi

# Ensure there are at least 6k products
# (the current number is at least twice that value)
test-min-rows-ncm: /data/trades.db
	@$(eval min_rows=6000)
	@$(eval n_rows=$(shell sql2csv -vH --db "$$DATABASE_URL" --query="SELECT COUNT(*) FROM ncm"))
	@if [ "$(n_rows)" -ge "$(min_rows)" ]; then \
		echo "OK: There are at least $(min_rows) product rows in table 'ncm'"; \
	else \
		echo "ERROR: The table 'uf' has $(n_rows) rows but it should have at least $(min_rows)"; \
		exit 1; \
	fi

# Ensure there are at least 500k rows for each year
# (the current numbers are at least twice that value)
test-min-rows-import: /data/trades.db
	@$(eval min_rows=500000)
	@$(eval n_incomplete_years=$(shell sql2csv -vH --db "$$DATABASE_URL" --query="SELECT COUNT(*) c FROM (SELECT strftime(\"%Y\", DATA) year, COUNT(*) count FROM import GROUP BY year HAVING count < $(min_rows))"))
	@if [ "$(n_incomplete_years)" -eq "0" ]; then \
		echo "OK: There are at least $(min_rows) rows for each year in table 'import'"; \
	else \
		echo "ERROR: The table 'import' has fewer than $(min_rows) for some year"; \
		exit 1; \
	fi

test-min-rows-export: /data/trades.db
	@$(eval min_rows=500000)
	@$(eval n_incomplete_years=$(shell sql2csv -vH --db "$$DATABASE_URL" --query="SELECT COUNT(*) c FROM (SELECT strftime(\"%Y\", DATA) year, COUNT(*) count FROM export GROUP BY year HAVING count < $(min_rows))"))
	@if [ "$(n_incomplete_years)" -eq "0" ]; then \
		echo "OK: There are at least $(min_rows) rows for each year in table 'export'"; \
	else \
		echo "ERROR: The table 'export' has fewer than $(min_rows) for some year"; \
		exit 1; \
	fi

# Ensure at least ~30% of the products listed in 'ncm' table are present in the 'import' table
# (the current percentage is >60%)
test-min-distinct-prod-import: /data/trades.db
	@$(eval min_percentage=30)
	@$(eval percentage=$(shell sql2csv -vH --db "$$DATABASE_URL" --query="SELECT CAST(100 * (SELECT 1.0*COUNT(DISTINCT(CO_NCM)) FROM import) / (SELECT COUNT(*) count FROM ncm) AS INTEGER)"))
	@if [ "$(percentage)" -ge "$(min_percentage)" ]; then \
		echo "OK: At least $(min_percentage)% of the products from 'ncm' table are present in table 'import'"; \
	else \
		echo "ERROR: Less than $(min_percentage)% of the products from 'ncm' table are present in table 'import'"; \
		exit 1; \
	fi

# Ensure at least ~30% of the products listed in 'ncm' table are present in the 'export' table
# (the current percentage is >60%)
test-min-distinct-prod-export: /data/trades.db
	@$(eval min_percentage=30)
	@$(eval percentage=$(shell sql2csv -vH --db "$$DATABASE_URL" --query="SELECT CAST(100 * (SELECT 1.0*COUNT(DISTINCT(CO_NCM)) FROM export) / (SELECT COUNT(*) count FROM ncm) AS INTEGER)"))
	@if [ "$(percentage)" -ge "$(min_percentage)" ]; then \
		echo "OK: At least $(min_percentage)% of the products from 'ncm' table are present in table 'export'"; \
	else \
		echo "ERROR: Less than $(min_percentage)% of the products from 'ncm' table are present in table 'export'"; \
		exit 1; \
	fi

# Ensure no group has more than 1 total price
test-max-total-prices-yearly: /data/trades.db
	@$(eval multiple_totals=$(shell sql2csv -vH --db "$$DATABASE_URL" --query="SELECT COUNT(*) FROM (SELECT kind, year, federative_unit, product, COUNT(*) count FROM top_by_state_and_year GROUP BY kind, year, federative_unit, product HAVING count > 1)"))
	@if [ "$(multiple_totals)" -eq "0" ]; then \
		echo "OK: There is at most one total price per combination of (kind of transaction, year, federative_unit and product)."; \
	else \
		echo "ERROR: Some combination of (kind of transaction, year, federative_unit and product) has more than one total price."; \
		exit 1; \
	fi

# Ensure no group has more than 1 total price
test-max-total-prices-monthly: /data/trades.db
	@$(eval multiple_totals=$(shell sql2csv -vH --db "$$DATABASE_URL" --query="SELECT COUNT(*) FROM (SELECT kind, year, month, federative_unit, product, COUNT(*) count FROM top_by_state_and_month GROUP BY kind, year, month, federative_unit, product HAVING count > 1)"))
	@if [ "$(multiple_totals)" -eq "0" ]; then \
		echo "OK: There is at most one total price per combination of (kind of transaction, year, month, federative_unit and product)."; \
	else \
		echo "ERROR: Some combination of (kind of transaction, year, month, federative_unit and product) has more than one total price."; \
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
