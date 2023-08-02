import pandas as pd
from colour import Color
import math
import json
import numpy as np

df = pd.read_pickle(r'correlation file of patient')
df_all = pd.read_pickle(r'correlation file of population')
cat = pd.read_json(r'concepts, parents and cat patient')
cat_all = pd.read_pickle(r'concepts, parents and cat patient and population')
cat_all = list(cat_all['concept'])
# df = pd.DataFrame({"concepta": ['a', 'a', 'a', 'b', 'b', 'b', 'c', 'c', 'c'], 
#     "conceptb": ['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c'], 
#     "val": [0, 1, 4, 1, 0, 0, 4, 0, 0], "notes": [[0],[1],[2,4],[1],[0], [0], [2,4], [0], [0]]})

# df_all = pd.DataFrame({"concepta": ['a', 'a', 'a', 'a', 'b', 'b', 'b', 'b', 'c', 'c', 'c', 'c', 'd', 'd', 'd', 'd'], 
#     "conceptb": ['a', 'b', 'c', 'd', 'a', 'b', 'c','d', 'a', 'b', 'c', 'd', 'a', 'b', 'c', 'd'], 
#     "val": [0, 2, 5, 1, 2, 0, 3, 2, 5, 3, 0, 6, 1, 2, 6, 0]})

print(df)
print(df_all)

# max_val_all = 0

# for index, row in df.iterrows():
#     print(index)
#     tmp = df_all.loc[(df_all['concepta'] == row['concepta']) & 
#             (df_all['conceptb'] == row['conceptb']), 'val']
#     if list(tmp): #check if entry exist in population
#         tmp = int(list(tmp)[0])
#     else:
#         tmp = 0
#     if (tmp > max_val_all):
#         max_val_all = tmp +1

#Make colorscale with max value steps from 0.000001 (0 mapped to this) to 1 (max val mapped to this) 
# to this in d3 this is linear one
# print(max_val_all)

#color for the max value steps along the axis
# blue_one = list(Color('#ece7f2').range_to(Color('#a6bddb'), math.floor(max_val_all/2)))
# blue_two = list(Color('#a6bddb').range_to(Color('#2b8cbe'), math.ceil(max_val_all/2)))
# blue = blue_one + blue_two

df_final = pd.DataFrame(columns=["concepta", "conceptb", "val", "notes", 'group'])
cat_patient = list(cat['concept'])
only_in_patient_concept = []
for cat in cat_patient:
    if cat not in cat_all:
        only_in_patient_concept.append(cat)
print(only_in_patient_concept)
print(len(only_in_patient_concept))

# prev_val = ''
# current_val = ''
# total_freq = {}
# total_val = 0
# for index, row in df.iterrows():
#     print(index)
#     current_val = row['concepta']
#     if(current_val != prev_val):
#         patient = True #side of the diagonal that is patient data
#         if prev_val != '':
#             total_freq[prev_val] = total_val
#         total_val = 0
#     if (row['concepta'] == row['conceptb']):
#         patient = False 
#         new_row = {"concepta": row['concepta'], "conceptb": row['concepta'], 
#             "val": 0, "notes": [-1], 'group': 'diagonal'}
#         df_final = df_final.append(new_row, ignore_index=True)
#     else: 
#         if patient:
#             tmp = int(row['val'])
#             new_row = {"concepta": row['concepta'], "conceptb": row['conceptb'], 
#                 "val": tmp, "notes": row['notes'], 'group': 'patient'}
#             df_final = df_final.append(new_row, ignore_index=True)
#             total_val += tmp
#         else: # population            
#             if(row['concepta'] not in only_in_patient_concept and 
#                 row['conceptb'] not in only_in_patient_concept):
#                 indexa = cat_all.index(row['concepta'])
#                 indexb = cat_all.index(row['conceptb'])
#                 index = (5410 * indexa) + indexb
#                 freq_all = df_all.iat[index, 2]
#             else:
#                 freq_all = 0
#             # freq_all = df_all.loc[(df_all['concepta'] == row['concepta']) & (df_all['conceptb'] == row['conceptb']), 'val']
#             # if list(freq_all): #check if entry exist in population
#             #     freq_all = int(list(freq_all)[0])
#             # else:
#             #     freq_all = 0
#             new_row = {"concepta": row['concepta'], "conceptb": row['conceptb'], 
#                 "val": freq_all, "notes": row['notes'], 'group': 'population'}
#             df_final = df_final.append(new_row, ignore_index=True)
#     prev_val = current_val


# total_freq = {k: v for k, v in sorted(total_freq.items(), key=lambda item: item[1])}
# print(total_freq)

def aggregate(df_final):
    val = 0
    val_pop = 0
    data = {}
    notes = []
    df_final_cat = pd.DataFrame(columns=["concepta", "conceptb", "val", "notes", 'group'])
    categories = list(set(cat['category']))
    categories.sort()
    print(categories)
    print(len(categories))
    for cata in categories:
        concepts_cata = list(cat.loc[cat['category'] == cata, 'concept'])
        print(cata)
        for catb in categories:
            print('CATB')
            print(catb)
            data_array = []
            concepts_catb = list(cat.loc[cat['category'] == catb, 'concept'])
            if (cata == catb):
                #diagonal                
                for index, row in df_final.iterrows():
                    if(row['concepta'] in concepts_cata and row['conceptb'] in concepts_catb):
                        tmp = []
                        for note in row['notes']: #make it json convertable
                            tmp.append(int(note))
                        data_array.append({"concepta": row["concepta"], "conceptb": row["conceptb"], 
                            "val": row["val"], "notes": tmp, 
                            "group": row['group']})
                        if(row['group'] == 'population'):
                            val_pop += row['val']
                        elif (row['group'] == 'patient'):
                            val += row['val']
                            if row['notes'] != [-1]:
                                notes += row['notes']
                new_row = {"concepta": cata, "conceptb": catb, 
                "val": [val, val_pop], "notes": notes, 'group': 'diagonal'}
                df_final_cat = df_final_cat.append(new_row, ignore_index=True)
                val = 0
                val_pop = 0
                notes = []
            else:                 
                # count patient or population   
                group = ''                 
                for index, row in df_final.iterrows():
                    if(row['concepta'] in concepts_cata and row['conceptb'] in concepts_catb):
                        tmp = []
                        for note in row['notes']: #make it json convertable
                            tmp.append(int(note))
                        data_array.append({"concepta": row["concepta"], "conceptb": row["conceptb"], 
                            "val": row["val"], "notes": tmp,  
                            "group": row['group']})
                        group = row['group']
                        val += row['val']
                        if row['notes'] != [-1]:
                            notes += row['notes']
                new_row = {"concepta": cata, "conceptb": catb, 
                "val": val, "notes": notes,  'group': group}
                df_final_cat = df_final_cat.append(new_row, ignore_index=True)
                val = 0
                notes = []            
            data[cata + ';' + catb] = data_array
    
    # max_val_pop = 0

    # for index, row in df_final_cat.iterrows():
    #     if row['group'] == 'diagonal':
    #         if (row['val'][1] > max_val_pop):
    #             max_val_pop = row['val'][1] +1
    #     elif row['group'] == 'population':
    #         if (row['val'] > max_val_pop):
    #             max_val_pop = row['val'] +1
    # print(max_val_pop)
    # blue_one = list(Color('#ece7f2').range_to(Color('#a6bddb'), math.floor(max_val_pop/2)))
    # blue_two = list(Color('#a6bddb').range_to(Color('#2b8cbe'), math.ceil(max_val_pop/2)))
    # blue = blue_one + blue_two
    # #fill in colors
    # for index, row in df_final_cat.iterrows():
    #     if row['group'] == 'diagonal':
    #         df_final_cat.at[index, 'color'] = [blue[row['val'][0]].hex, blue[row['val'][1]].hex]
    #     else:
    #         df_final_cat.at[index, 'color'] = blue[row['val']].hex
    return df_final_cat, data

df_final_cat, data = aggregate(df_final)

with open(r'fill in path', 'w') as outfile:
    json.dump(data, outfile)

data_json = []
for index, row in df_final_cat.iterrows():
    tmp = []
    for note in row['notes']: #make it json convertable
        tmp.append(int(note))
    data_json.append({"concepta": row["concepta"],  "conceptb": row["conceptb"], 
        "val": row["val"], "notes": tmp, "group": [row['group']]})
#print(data_json)

with open(r'fill in path', 'w') as outfile:
    json.dump(data_json, outfile)

