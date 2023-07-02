#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


# erstes CSV einlesen mit den Log-Daten
log_data = pd.read_csv('RTWIBNet_W22_log.csv')

# zweites CSV einlesen mit den Abschlussnoten
grade_data = pd.read_csv('RTWIBNet_W22_grades.csv')

log_data.head()
#grade_data.head()


# In[3]:


log_data.info()


# In[4]:


# eindeutige Werte der Spalten 'Voll.Name', 'Komponente', 'Herkunft' von sim_data als array ausgeben 

unique_name = log_data['Vollständiger Name'].unique()
unique_komponente = log_data['Komponente'].unique()
unique_herkunft = log_data['Herkunft'].unique()

# länge der Arrays ausgeben 

length_name = len(unique_name)
length_komponente = len(unique_komponente)
length_herkunft = len(unique_herkunft)


# In[5]:


# neues df mit Auswertparameter von sim_data nach Spalte 'Vollständiger Name' erstellen
# pro eindeutiger Parameter in den Spalten 'Komponente' und 'Herkunft' soll eine neue Spalte in grouped_sim erstellen werden
# Hierzu beziehen wir uns auf die zuvor erstellen arrays mit der Anzahl der eindeutigen Werte einer Spalte unique_komponente
# Nur so viele neue Spalten werden generiert, wie es eindeutige Werte pro Spalte hat
# Der Name der neuen Spalte entspricht 'Anzahl' + Name eindeutiger Wert 

# Spalten 'Komponente' und 'Herkunft' als String konvertieren
log_data['Herkunft'] = log_data['Herkunft'].astype(str)
log_data['Komponente'] = log_data['Komponente'].astype(str)

# Neues gruppiertes DataFrame erstellen und Index zurücksetzen
grouped_data = log_data.groupby('Vollständiger Name').agg({
    'Komponente': [(f'Anzahl {name}', lambda x, name=name: (x == name).sum()) for name in unique_komponente],
    'Herkunft': [(f'Anzahl {name}', lambda x, name=name: (x == name).sum()) for name in unique_herkunft],
    'IP-Adresse': 'nunique'
}).reset_index()

grouped_data


# In[6]:


# Check Anzahl der Studierende

len(grouped_data['Vollständiger Name'])


# In[7]:


from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, "de_DE") # german
'de_DE'

# Anzahl der Vorkommen eines Users im ursprünglichen sim_data
user_counts = log_data['Vollständiger Name'].value_counts().rename('Anzahl_log_all')

# nur das Datum extrahieren
log_data['Zeit'] = pd.to_datetime(log_data['Zeit'], format='%d. %B %Y, %H:%M:%S').dt.date

# Definiere den Start- und Endzeitpunkt für den ersten Zeitraum
# Start: erster Log-Eintrag
start_date = log_data['Zeit'].min()

# 16 Wochen später als der erste Eintrag (Dauer eines Semesters)
end_date = start_date + pd.DateOffset(weeks=20)
# Beobachtung: teilweise Einträge nach 16 Wochen - Enddatum = Letzter Log-Eintrag der Logdatei
#end_date = log_data['Zeit'].max()

# Definiere den Zeitraumabstand
period_offset = pd.DateOffset(weeks=2)

# Liste zur Speicherung der Zeitraumgrenzen
period_boundaries = []

# Generiere die Zeitraumgrenzen mit einem Abstand von zwei Wochen
# pro Zeitraumgrenze wird es eine neue Spalte in dem DataFrame log_counts geben
# Wenn keine Werte für die Zeiträume z.B. bei 16 Wochen vorhanden sind, werden die Spalten mit dem Mittelwert der vorherigen
# Zeitraumsgrenzen aufgefüllt

current_date = start_date
while current_date <= end_date:
    period_boundaries.append(current_date)
    current_date += period_offset

# Erstelle das DataFrame log_counts mit den Zeitraumspalten
log_counts = pd.DataFrame()
log_counts['Vollständiger Name'] = user_counts.index.unique() # Eindeutige Namen im Index verwenden
log_counts['Anzahl_log_all'] = user_counts.reindex(log_counts['Vollständiger Name']).values # Werte entsprechend den eindeutigen Namen im Index reindexieren

# Überprüfung des letzten Datums in sim_data
last_date = log_data['Zeit'].max()

# Auffüllen der fehlenden Zeiträume basierend auf dem letzten Datum
for i in range(len(period_boundaries)):
    period_start = period_boundaries[i]
    if i == len(period_boundaries) - 1:
        # Letzter Zeitraum, fiktiven Wert verwenden - Mittelwert der vorherigen Zeiträume
        log_counts[f'Anzahl_log_f{i+1}'] = np.mean(log_counts[[f'Anzahl_log_f{j}' for j in range(1, i+1)]], axis=1).astype(int)
    else:
        period_end = period_boundaries[i + 1]
        
        if last_date >= period_end:
            # Datum liegt im Zeitraum, Log-Einträge zählen
            log_entries_by_period = log_data[(log_data['Zeit'] >= period_start) & (log_data['Zeit'] < period_end)].groupby('Vollständiger Name').count()
            log_counts[f'Anzahl_log_f{i+1}'] = log_entries_by_period['Zeit'].reindex(log_counts['Vollständiger Name'], fill_value=0).values
        else:
            # Datum liegt außerhalb des Zeitraums, mit Mittelwert auffüllen als Ganzzahl
            log_counts[f'Anzahl_log_f{i+1}'] = np.mean(log_counts[[f'Anzahl_log_f{j}' for j in range(1, i+1)]], axis=1).astype(int)

log_counts.head()


# In[8]:


# Anzahl log-Einträge mit sim_data mergen nach 'Vollständiger Name'
grouped_data_log = grouped_data.merge(log_counts, on='Vollständiger Name')

grouped_data_log.head()


# In[9]:


# Vollständiger Name doppelt - zweite Spalte droppen
grouped_data_log = grouped_data_log.drop(('Vollständiger Name', ''), axis=1)
grouped_data_log


# In[10]:


# Übersicht über 2. df mit Note grade_data
grade_data


# In[11]:


def check_grades(grade_csv):
    if grade_csv['bewertung'].isnull().any():
        # Wenn die Spalte 'bewertung' leer ist > Produktionsdaten, keine Trainingsdaten
        
        # gleich als CSV file abspeichern
        grouped_data_log.to_csv('grouped_data_log.csv', index=False)
        return grouped_data_log.head()
    
    
    else:
        # ansonsten Spalte mit den Noten anpassen:
        # Bewertung / 100 ergibt die Schulnote
        grade_csv['bewertung'] = grade_csv['bewertung']/100
        
        # Wenn es zu dem User keine Bewertung gibt - ersetzte NaN mit 5.0
        grade_csv['bewertung'] = grade_csv['bewertung'].fillna(5.0)
        
        # Abschlussnote aus dem zweiten df grade_data_log dem jeweiligen User zuordnen
        grouped_data_grade = pd.merge(grouped_data_log, grade_csv, on='Vollständiger Name', how='left')
        
        # Als CSV-file abspeichern
        grouped_data_grade.to_csv('grouped_data_grade.csv', index=False)
        
        return grouped_data_grade.head()


# In[12]:


check_grades(grade_data)


# In[13]:


# In Methode integriert
# Wenn es zu dem User keine Bewertung gibt - ersetzte NaN mit 5.0
# grade_data['bewertung'] = grade_data['bewertung'].fillna(5.0)
# grade_data


# In[14]:


# In Methode integriert

# Abschlussnote aus dem zweiten df grade_data_log dem jeweiligen User zuordnen

# grouped_data_grade = pd.merge(grouped_data_log, grade_data, on='Vollständiger Name', how='left')

# grouped_data_grade.head()

