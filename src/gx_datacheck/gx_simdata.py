import great_expectations as gx
import pandas as pd
import numpy as np
import os

# Check if environment variable is set otherwise set it to default
# Input variables
if 'SIMDATA_FILENAME' in os.environ:
    SIMDATA_FILENAME = os.environ['SIMDATA_FILENAME']
else:    
    SIMDATA_FILENAME = '/app/data/00_simdata/00_simdata.csv'
# Output variables
if 'GX_SIMDATA_FILENAME' in os.environ:
    GX_SIMDATA_FILENAME = os.environ['GX_SIMDATA_FILENAME']
else:
    GX_SIMDATA_FILENAME = '01_gx_simdata.csv'
if 'GX_SIMDATA_PATH' in os.environ:
    GX_SIMDATA_PATH = os.environ['GX_SIMDATA_PATH']
else:
    GX_SIMDATA_PATH = '/app/data/01_gx'

context = gx.get_context()

validator = context.sources.pandas_default.read_csv(SIMDATA_FILENAME)

# #### Anforderungen festlegen (können beliebig viele sein)

# über den Befehl 'great_expectations suite list' im  kann überprüft werden, welche Expectations 
# für eine Datei definiert worden sind - die list muss aber vorab erst erstellt werden (Sammlung)

# Anforderung 1: keine Nullwerte
validator.expect_column_values_to_not_be_null('Zeit')
validator.expect_column_values_to_not_be_null('Vollständiger Name')
validator.expect_column_values_to_not_be_null('Komponente')
validator.expect_column_values_to_not_be_null('Herkunft')
validator.expect_column_values_to_not_be_null('IP-Adresse')

# Anforderung 2: Spalte 'Herkunft' soll vom Datentyp string sein
# > rausgenommen! Soll für datacheck 1 und datacheck 2 identischer Code sein
#validator.expect_column_values_to_be_of_type('Herkunft', type_= 'str')

# #### Daten auf Basis der Anforderungen validieren 

checkpoint = gx.checkpoint.SimpleCheckpoint(
    name="checkpoint",
    data_context=context,
    validator=validator,
)

checkpoint_result = checkpoint.run()

# #### Ergebnis der Validierung ausgeben lassen 
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
    data.to_csv(new_filepath, index=False)
    #data.to_csv(new_filepath, index=False)
    print(f'Die CSV  wurde unter {filename} als CSV Datei gespeichert.')

if checkpoint_result["success"]:
    print("Die Expectations wurden erfüllt. Die relevanten Spalten 'Zeit', 'Vollständiger Name', 'Komponente', 'Herkunft', und 'IP-Adresse' enthalten keine Nullwerte.")
    sim_data = pd.read_csv(SIMDATA_FILENAME)
    save_file_with_version(GX_SIMDATA_FILENAME, GX_SIMDATA_PATH, sim_data)
else:
    print("Die Expectations wurden nicht erfüllt.")