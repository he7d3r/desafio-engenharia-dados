#!/bin/bash

# TODO: Create the tables first, with proper column types, then:
# csvsql $CSV --db $DB --insert --no-create --tables $TABLE
# See e.g.:
# https://github.com/ALLIANCETECHSYSTEM/CovidBRdb/blob/master/scripts/db_build.sh
# https://github.com/ALLIANCETECHSYSTEM/CovidBRdb/blob/master/scripts/db_populate.sh

csvsql --db "sqlite:///data/imp_2017.db" --insert data/IMP_2017.csv
csvsql --db "sqlite:///data/imp_2018.db" --insert data/IMP_2018.csv
csvsql --db "sqlite:///data/imp_2019.db" --insert data/IMP_2019.csv

csvsql --db "sqlite:///data/exp_2017.db" --insert data/EXP_2017.csv
csvsql --db "sqlite:///data/exp_2018.db" --insert data/EXP_2018.csv
csvsql --db "sqlite:///data/exp_2019.db" --insert data/EXP_2019.csv