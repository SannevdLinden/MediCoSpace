import pandas as pd
import numpy as np 

def get_df(patient):
    df = pd.read_pickle(r'path to patient data file')
    #df = df.loc[df['category'] == 'procedure']
    return df

df2 = get_df('patient id 1')
df3 = get_df('patient id 2')
#....

procedure = pd.concat([df2, df3]) #and more for all patients
print(procedure)

procedures_grouped = procedure.groupby(['parent'], dropna=False)
print(procedures_grouped)
all_drugs = []
exceptions = ['Fetal measurement and monitoring']
unique_drugs = set()
#pd.set_option('display.max_columns', None)
for key, item in procedures_grouped:
    tmp = set()
    for row_index, row in item.iterrows():
        if row['concept'] not in unique_drugs and row['parent']:
            tmp.add(row['concept'])
            unique_drugs.add(row['concept'])
    all_drugs += sorted(list(tmp))

print(all_drugs)
print(len(all_drugs))
all_drugs = all_drugs

category = []
label = []
for drug in all_drugs:
    tmp = procedure.loc[procedure['concept'] == drug, ['parent', 'category']]
    category.append(list(tmp.head(1)['parent'])[0])
    label.append(list(tmp.head(1)['category'])[0])
print(category)

cat_df = pd.DataFrame({
    'concept': all_drugs,
    'category': category, 
    'label': label
})
cat_df.to_pickle(r'fill in path')
cat_df.to_json(r'fill in path')
print(cat_df)

#count for each drug tuple how often they co-occur
# values = np.array([])
# count = 0
# for druga in all_drugs:
#     print(count)
#     count += 1
#     notes_druga = procedure.loc[procedure['concept'] == druga, 'note_id']
#     for drugb in all_drugs:
#         if druga == drugb:
#             values = np.append(values, [0])
#         else:
#             notes_druga = np.array(notes_druga)
#             notes_drugb = procedure.loc[procedure['concept'] == drugb, 'note_id']
#             notes_drugb = np.array(list(notes_drugb))
#             intersect = np.intersect1d(notes_druga, notes_drugb)
#             if(intersect.size == 0):
#                 values = np.append(values, [0])
#             else:
#                 values = np.append(values, [intersect.size])

# length = len(all_drugs)
# drug_for_df = []
# counter2 = 0
# for drug in all_drugs:
#     print(counter2)
#     counter2 += 1
#     for i in range(length):
#         drug_for_df.append(drug)

# print('One down')

# counter3 = 0
# drug_for_df_colb = []
# for j in range(len(all_drugs)):
#     print(counter3)
#     counter3 += 1
#     drug_for_df_colb += all_drugs

# print('two down')

# dummie_df = pd.DataFrame({"concepta": drug_for_df,
#                    "conceptb": drug_for_df_colb,
#                    "val": values})
# dummie_df.to_pickle(r'fill in')
# dummie_df.to_json(r'fill in')

# print(dummie_df)
