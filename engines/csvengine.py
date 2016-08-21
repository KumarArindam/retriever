from builtins import str
from builtins import object

import os

from retriever.lib.models import Engine
from retriever import DATA_DIR
from retriever.lib.tools import sort_csv


class DummyConnection(object):

    def cursor(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


class DummyCursor(DummyConnection):
    pass


class engine(Engine):
    """Engine instance for writing data to a CSV file."""
    name = "CSV"
    abbreviation = "csv"
    datatypes = {
        "auto": "INTEGER",
        "int": "INTEGER",
        "bigint": "INTEGER",
        "double": "REAL",
        "decimal": "REAL",
        "char": "TEXT",
        "bool": "INTEGER",
    }
    required_opts = [
        ("table_name",
         "Format of table name",
         os.path.join(DATA_DIR, "{db}_{table}.csv")),
    ]

    def create_db(self):
        """Override create_db since there is no database just a CSV file"""
        return None

    def create_table(self):
        """Create the table by creating an empty csv file"""
        self.auto_column_number = 1
        self.output_file = open(self.table_name(), "w")
        self.output_file.write(
            ','.join(['"%s"' % c for c in self.table.get_insert_columns(join=False,create=True)]))

    def disconnect(self):
        """Close the last file in the dataset"""
        try:
            self.output_file.close()
        except:
            # when disconnect is called by app.connect_wizard.ConfirmPage to
            # confirm the connection, output_file doesn't exist yet, this is
            # fine so just pass
            pass

    def execute(self, statement, commit=True):
        """Write a line to the output file"""
        self.output_file.write('\n' + statement)

    def format_insert_value(self, value, datatype):
        """Formats a value for an insert statement"""
        v = Engine.format_insert_value(self, value, datatype, escape=False)
        if v == 'null':
            return ""
        try:
            if len(v) > 1 and v[0] == v[-1] == "'":
                v = '"%s"' % v[1:-1]
        except:
            pass
        return v

    def insert_statement(self, values):
        """Returns a comma delimited row of values"""

        if not hasattr(self, 'auto_column_number'):
            self.auto_column_number = 1
        insert_stmt = ','.join([str(value) for value in values])
        if self.table.columns[0][1][0][3:] == 'auto':
            insert_stmt = str(self.auto_column_number) + "," + insert_stmt
            self.auto_column_number += 1
        return insert_stmt

    def table_exists(self, dbname, tablename):
        """Check to see if the data file currently exists"""
        tablename = self.table_name(name=tablename, dbname=dbname)
        return os.path.exists(tablename)

    def to_csv(self):
        """Export sorted version of CSV file"""
        return sort_csv(self.table_name())

    def get_connection(self):
        """Gets the db connection."""
        self.get_input()
        return DummyConnection()
