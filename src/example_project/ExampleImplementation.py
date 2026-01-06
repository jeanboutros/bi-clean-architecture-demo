# Databricks notebook source
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2
# MAGIC # Enables autoreload; learn more at https://docs.databricks.com/en/files/workspace-modules.html#autoreload-for-python-modules
# MAGIC # To disable autoreload; run %autoreload 0

# COMMAND ----------

import sys, os
current_path = os.path.abspath('')
project_path = os.path.dirname(current_path)

if current_path in sys.path:
    print('Removing project path from sys.path to force the imports to start with the project package name', current_path)
    sys.path.remove(current_path)

if project_path not in sys.path:
    print('Adding project path to sys.path to mimick a project being installed as a library:', project_path)
    sys.path.append(project_path)

print("Current path:", current_path)
print("Project path:", project_path)
print("sys.path:", '
'.join(sys.path))

# COMMAND ----------

from example_project.composition.frames import ingest_frames_from_api_into_landing_layer
from example_project.composition.context import Context

notebook_context = Context.notebook_default()

ingest_frames_from_api_into_landing_layer(context=notebook_context)

# COMMAND ----------

!cat /Volumes/dev_catalog_base/default/sales-reporting-gen2-temp/landing_layer_test/2025_file.json

# COMMAND ----------

