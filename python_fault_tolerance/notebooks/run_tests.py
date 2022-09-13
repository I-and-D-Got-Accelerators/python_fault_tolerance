# Databricks notebook source
import pytest
import os
import sys

# COMMAND ----------

# Quick solution to add ../src to path.
sys.path.append('/Workspace/Repos/fault_tolerance/python_fault_tolerance/python_fault_tolerance/src')
#print("\n".join(sys.path))

# COMMAND ----------

# Run all tests in the repository root regardless of where we are
notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()

repo_root = os.path.dirname(os.path.dirname(notebook_path))

os.chdir(f'/Workspace/{repo_root}') # Requires permission to change folder

# Skip writing pyc files on a readonly filesystem.
sys.dont_write_bytecode = True

# Run pytest main. Remove --html or pip install pytest-html
retcode = pytest.main([".", "-v", "-l", "--html", "/dbfs/tmp/report.html", "--self-contained-html", "-p", "no:cacheprovider"]) # Returns Exit code

# COMMAND ----------

# Read HTML report of pytest
html_file = open("/dbfs/tmp/report.html", 'r').read()
displayHTML(html_file)

# COMMAND ----------

print(retcode)
