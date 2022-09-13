# Databricks notebook source
import pytest
import os
import sys

# COMMAND ----------

print("\n".join(sys.path))

# COMMAND ----------

# Run all tests in the repository root.
notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()

#repo_root = os.path.dirname(os.path.dirname(notebook_path))

#print(notebook_path)
#print(repo_root)

#os.chdir(f'/Workspace/{repo_root}') # PERMISSIONERROR

# Skip writing pyc files on a readonly filesystem.
#sys.dont_write_bytecode = True

retcode = pytest.main([".", "-p", "no:cacheprovider"])
