import great_expectations as gx
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sns
#%matplotlib inline


# ### 1) Test - vertraut machen mit gx; Expectations manuell programmieren

# #### DataContext erstellen

# In[2]:


context = gx.get_context()


# In[3]:


validator = context.sources.pandas_default.read_csv('/home/jovyan/00_sim_data_output/simulated_data_grade.csv')


# #### Anforderungen festlegen (können beliebig viele sein)

# In[14]:


# über den Befehl 'great_expectations suite list' im  kann überprüft werden, welche Expectations 
# für eine Datei definiert worden sind - die list muss aber vorab erst erstellt werden (Sammlung)


# In[4]:


# Anforderung 1: die Spalte 'Zeit' soll nie gleich Null sein
validator.expect_column_values_to_not_be_null('Zeit')


# In[5]:


# Anforderung 2: Spalte 'Herkunft' soll vom Datentyp string sein
validator.expect_column_values_to_be_of_type('Herkunft', type_= 'str')


# #### Daten auf Basis der Anforderungen validieren 

# In[6]:


checkpoint = gx.checkpoint.SimpleCheckpoint(
    name="checkpoint",
    data_context=context,
    validator=validator,
)


# In[7]:


checkpoint_result = checkpoint.run()


# In[42]:


# Alternative Programmierung: result = validator.validate()


# #### Ergebnis der Validierung ausgeben lassen 

# In[12]:


import os
import pandas as pd

filename = 'sim_data.parquet'
container_path = '/home/jovyan/01_sim_data_parquet'

def save_file_with_version(filename, container_path, data):
# Überprüfe, ob die Datei bereits existiert
    if os.path.exists(os.path.join(container_path, filename)):
        base_name, ext = os.path.splitext(filename)
        version = 3

        while True:
            # Erzeuge den neuen Dateinamen mit fortlaufender Nummer
            new_filename = f"{base_name}_V{version}{ext}"
            new_filepath = os.path.join(container_path, new_filename)

            if not os.path.exists(new_filepath):
                break

            version += 1

        # Benenne die bestehende Datei um
        os.rename(os.path.join(container_path, filename), new_filepath)
        print(f'Die Datei {filename} wurde umbenannt zu {new_filename}.')

    # Speichere das DataFrame als CSV-Datei unter dem ursprünglichen Dateinamen
    new_filepath = os.path.join(container_path, filename)
    data.to_parquet(new_filepath, index=False)
    print(f'Die CSV  wurde als Parquet-Datei unter {filename} gespeichert.')


if checkpoint_result["success"]:
    print("Die Expectations Spalte 'Zeit' != Null und Spalte 'Herkunft' von Datentyp string wurden erfüllt.")
    sim_data = pd.read_csv('/home/jovyan/00_sim_data_output/simulated_data_grade.csv')
    save_file_with_version(filename, container_path, sim_data)
else:
    print("Die Expectations wurden nicht erfüllt. Das Dataframe wurde nicht als Parquet-file gespeichert.")

# ### Liste an möglichen Anforderungen, die definiert werden können:
# 
# expect_column_values_to_be_null(column): 
# Überprüft, ob die Werte in einer Spalte Null sind.
# 
# expect_column_values_to_not_be_null(column): 
# Überprüft, ob die Werte in einer Spalte nicht Null sind.
# 
# expect_column_values_to_be_unique(column): 
# Überprüft, ob die Werte in einer Spalte eindeutig sind.
# 
# expect_column_values_to_be_in_set(column, value_set): 
# Überprüft, ob die Werte in einer Spalte in einem bestimmten Werteset enthalten sind.
# 
# expect_column_values_to_be_between(column, min_value, max_value): 
# Überprüft, ob die Werte in einer Spalte innerhalb eines bestimmten Wertebereichs liegen.
# 
# expect_column_values_to_match_regex(column, regex): 
# Überprüft, ob die Werte in einer Spalte einem bestimmten regulären Ausdruck entsprechen.
# 
# expect_column_values_to_be_of_type(column, data_type): 
# Überprüft, ob die Werte in einer Spalte einem bestimmten Datentyp entsprechen.
# 
# expect_table_row_count_to_be_between(min_value, max_value): 
# Überprüft, ob die Anzahl der Zeilen in einer Tabelle innerhalb eines bestimmten Bereichs liegt.
# 
# expect_table_columns_to_match_ordered_list(column_list): 
# Überprüft, ob die Spalten in einer Tabelle der angegebenen geordneten Liste entsprechen.
# 
# expect_table_columns_to_match_set(column_set): 
# Überprüft, ob die Spalten in einer Tabelle dem angegebenen Spaltenset entsprechen.
# 
# expect_column_values_to_be_of_type("column", data_type="integer")
# Überprüft, ob die Spalte von einem bestimmten Datentyp ist (hier: integer) 

# ### 2) Test-Suits erstellen / testen

# #### im Terminal Test-Suite erstellen:
# ##### great_expectations suite new > Name eingeben 
# 
# #### Suite-Datei öffnen und bearbeiten, um Anforderungen bearbeiten zu können: 
# ##### great_expectations suite edit great_expectations/expectations/NewExpectationSuite.json

# #### im Browser dieses file öffnen - dies ist die Test-Suite im JupyterNotebook! 
# ##### # file:///C:/Users/Tami/AppData/Roaming/jupyter/runtime/nbserver-23492-open.html
# 
# ##### >> Expectations raussuchen und einfügen - s. https://greatexpectations.io/expectations/ 

