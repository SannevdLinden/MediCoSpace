## the code was inspired by the master thesis from Fabian Viehmann
from torch.utils.data import DataLoader
import math
from sentence_transformers import SentenceTransformer,  LoggingHandler, losses, models, util
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from sentence_transformers.readers import InputExample
import logging
from datetime import datetime
import json
import pandas as pd
import numpy as np
import re
import spacy
from scipy.spatial.distance import cdist
from umap import UMAP
nlp = spacy.load("en_core_sci_lg")

##language model
#model training code from https://github.com/UKPLab/sentence-transformers/blob/master/examples/training/sts/training_stsbenchmark.py
#only loading the data differs
#need to add your paths
def train_language_model():
  logging.basicConfig(format='%(asctime)s - %(message)s',
                  datefmt='%Y-%m-%d %H:%M:%S',
                  level=logging.INFO,
                  handlers=[LoggingHandler()])
  
  model_name = r"path to clinical_kb_bert" 
  #the other tree models we used to compare are recognized by library, e.g., 
  #'gsarti/biobert-nli', 'microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext', 'emilyalsentzer/Bio_ClinicalBERT'

  train_batch_size = 16
  num_epochs = 4
  model_save_path = r"path to folder for output\clinical_kb_bert_after_finetuning"
  word_embedding_model = models.Transformer(model_name)

  pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension(),
                              pooling_mode_mean_tokens=True,
                              pooling_mode_cls_token=False,
                              pooling_mode_max_tokens=False)

  model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

  train_samples = load_data('train')
  dev_samples = load_data('dev')
  test_samples = load_data('test')

  train_dataloader = DataLoader(train_samples, shuffle=True, batch_size=train_batch_size)
  train_loss = losses.CosineSimilarityLoss(model=model)
  
  logging.info("Read dev dataset")
  evaluator = EmbeddingSimilarityEvaluator.from_input_examples(dev_samples, name='dev')

  warmup_steps = math.ceil(len(train_dataloader) * num_epochs  * 0.1) 
  logging.info("Warmup-steps: {}".format(warmup_steps))

  model.fit(train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=num_epochs,
        evaluation_steps=1000,
        warmup_steps=warmup_steps,
        output_path=model_save_path)
  
  model = SentenceTransformer(model_save_path)
  test_evaluator = EmbeddingSimilarityEvaluator.from_input_examples(test_samples, name='test')
  test_evaluator(model, output_path=model_save_path)

def load_data(name):
  result = []
  path = ""
  if name == 'train':
    path = r'path to training jsonl file mednli'
  elif name == 'test':
    path = r'path to test jsonl file mednli'
  elif name == 'dev':
    path = r'path to dev jsonl file mednli'

  with open(path, 'r') as json_file:
      json_list = list(json_file)

  for json_str in json_list:
    line = json.loads(json_str)
    if line['gold_label'] == 'entailment':
      score = 1.0
    elif line['gold_label'] == 'neurtal':
      score = 0.5
    elif line['gold_label'] == 'contradiction':
      score = 0.0
    result.append(InputExample(texts=[line['sentence1'], line['sentence2']], label=score))
  return result  

##UMLS vector part
# you need to obtain a UMLS installation and license.
def umls_vectors():
  #get concepts from umls in relevant vocabularies
  cui = []
  aui = []
  name = []
  cat = []
 
  for line in generator_concepts():
    cui.append(line[0])
    aui.append(line[7])
    name.append(line[14])
    if line[11] == 'ICD10':
      cat.append('disease')
    elif line[11] == 'ATC':
      cat.append('drug')
    elif line[11] == 'CCS_10':
      cat.append('procedure')
  
  concepts = pd.DataFrame(list(zip(cui,aui,name,cat)), columns=['cui', 'aui', 'name', 'cat']) 
  concepts['name'] = concepts['name'].apply(text_cleaning)
  path = r'path to clinical kb model'
  model = SentenceTransformer(path)
  concepts['vector'] = concepts['name'].apply(lambda x: model.encode(x))
  #print(concepts)
  return concepts
  
def generator_concepts():
  path_to_mrconso =  r'path to concepts umls'
  file = open(path_to_mrconso, "r")
  for line in file:
    line = line.strip().split('|')
    #english concepts of relevant vocabs
    relevant_vocab = ['ICD10', 'ATC', 'CCS_10']
    #you can check the headers https://www.ncbi.nlm.nih.gov/books/NBK9685/
    if(line[1] == 'ENG' and line[11] in relevant_vocab): 
      yield line
    else: 
      continue

def text_cleaning(string_concept):
  string_concept = re.sub('([A-Z]{1,2})([0-9]{1,2})', '', string_concept)
  string_concept = string_concept.lower()  
  string_concept = re.sub('[^a-zA-Z0-9 ]', '', string_concept)
  string_concept = string_concept.strip()
    
  return string_concept

def note_concepts(vec_umls, patient):
  print('start processing patient ' + str(patient))
  path = r'path to patient notes'
  path_model = r'path to clinical kb model'
  cats = ['disease', 'drug', 'procedure']
  model = SentenceTransformer(path_model)
  df = pd.read_csv(path)  
  selection = df.loc[df["SUBJECT_ID"] == patient]
  dis_df = vec_umls[vec_umls['cat'] == 'disease'] 
  drug_df = vec_umls[vec_umls['cat'] == 'drug'] 
  pro_df = vec_umls[vec_umls['cat'] == 'procedure'] 

  #final df: note id, note tekst of concept, concept ontology, parent concept, cat 
  final_result = [[],[],[],[],[]]

  for index, row in selection.iterrows():
    note_text = row["TEXT"]
    #split text to sentences
    note_text = nlp(note_text).sents
    
    for sentence in note_text:
      raw_sentence = str(sentence)
      #clean note text
      sentence_clean = str(sentence).lower()
      #remove anonymized tags
      sentence_clean = re.sub('[[*]{2}.*?[*]{2}\]', '', sentence_clean)
      pot_con_sentence = sentence.ents
      sentence_vec = model.encode(sentence_clean)
      
      for c in cats:
        ind_con = [[],[]]
        if c == 'disease' and len(list(dis_df['vector'])) > 0:            
          df_tmp = dis_df['vector'] 
        elif c == 'drug' and len(list(drug_df['vector'])) > 0:
          df_tmp = drug_df['vector']
        elif c == 'procedure' and len(list(pro_df['vector'])) > 0:
          df_tmp = pro_df['vector']
            
        #potential concepts
        for ent in pot_con_sentence:
          #clean note text
          ent_clean = str(ent).lower()
          #remove anonymized tags
          ent_clean = re.sub('[[*]{2}.*?[*]{2}\]', '', ent_clean)
          vector_ent = model.encode(ent_clean)
          if not np.all(vector_ent==None) and not np.all(vector_ent==0):
            ind_con = concept_vector(vector_ent, list(df_tmp), ent_clean)
    
        #sentence vector
        if not np.all(sentence_vec==None) and not np.all(sentence_vec==0):
          tmp = concept_vector(sentence_vec, list(df_tmp), sentence_clean) 
          for i in range(len(tmp[0])):
            if tmp[0][i] not in ind_con[0]:
                ind_con[0].append(tmp[0][i])
                ind_con[1].append(raw_sentence) 
        
        #add to final df
        for i in range(len(ind_con[0])):
          final_result[0].append(index)
          final_result[1].append(ind_con[1][i])
          final_result[2].append(list(dis_df['name'])[i])
          final_result[3].append(list(dis_df['aui'])[i])
          final_result[4].append(c)
    
  return final_result


def concept_vector(vector, cat_vectors, text, threshold = 0.5):
  #calc the closest vector in the chosen concept space
  similarity = cdist([vector], cat_vectors, metric='cosine')
  distance = 1-np.abs(similarity)
  result = [[],[]]
  for scores in range(len(distance[0])):
    if distance[0][scores] > threshold:
      result[0].append(scores)
      result[1].append(text)
  return result

#get parent concept
def parent_concept(list_concepts):
  result_parents = []
  relevant_concepts =  list(set(list_concepts))
  convert_dict = {}
  name_dict = {}
  #only concepts that occur in notes
  for line in generator_concepts_hier(relevant_concepts):
    if len(line[6].split(".")) > 1:
      convert_dict[line[1]] = line[6].split(".")[1] #can pick which level of detail you want
    else:
      convert_dict[line[1]] = ''
  
  for line in generator_concepts():
    if line[7] in convert_dict:
      name_dict[line[7]] = line[14]
  
  for i in range(len(list_concepts)):
    if convert_dict[list_concepts[i]] != '':
      parent_aui = convert_dict[list_concepts[i]]
      parent_text = name_dict[parent_aui]
      result_parents.append(parent_text)
    else:
      result_parents.append('')   

  return result_parents


def generator_concepts_hier(relevant_concepts):
  path_to_mrhier =  r'path to hier file umls'
  file = open(path_to_mrhier, "r")
  for line in file:
    line = line.strip().split('|')
    #english concepts of relevant vocabs
    relevant_vocab = ['ICD10', 'ATC', 'CCS_10']
    #you can check the headers https://www.ncbi.nlm.nih.gov/books/NBK9685/
    if(line[4] in relevant_vocab): 
      if(line[1] in relevant_concepts): 
        yield line
      else: 
        continue
    else: 
      continue

def get_embedding(vec_umls, all_concepts, cat):
  relevant_concepts =  list(set(all_concepts[1]))
  relevant_vec = {}
  con_dict = {}
  result_embeddings = {"x":{}, "y":{}, "embeddings":{}}

  for c in relevant_concepts:
    relevant_vec[c] = []
  
  for index, row in vec_umls.iterrows():
    if row['aui'] in relevant_vec:
      relevant_vec[row['aui']] = row['vector']
      con_dict[row['aui']] = row['name']
  
  vecs = list(relevant_vec.values())
  umap_2d = UMAP()
  proj_2d = umap_2d.fit_transform(vecs)
  
  result_embeddings['x']['min'] = str(min(proj_2d[:, 0]))
  result_embeddings['x']['max'] = str(max(proj_2d[:, 0]))
  result_embeddings['y']['min'] = str(min(proj_2d[:, 1]))
  result_embeddings['y']['max'] = str(max(proj_2d[:, 1]))
  proj_2d = proj_2d[:2]

  concept = list(relevant_vec.keys())
  for i in range(len(proj_2d)):
    con_name = con_dict[concept[i]]
    result_embeddings['embeddings'][con_name] = [str(proj_2d[i][0]),str(proj_2d[i][1])]
  
  path_em = r'fill in path' 
  with open(path_em, "w") as outfile:
    json.dump(result_embeddings, outfile)

###########################
##  main part ############
#########################

#first fine tune the language model on MEDNLI (https://physionet.org/content/mednli/1.0.0/)
#train_language_model()

#get the umls vectors
vec_umls = umls_vectors()

#match vectors from medical notes
patient_ids = [] #mimic patient ids
all_concepts = [[],[],[]]
for patient in patient_ids:
  result = note_concepts(vec_umls, patient)
  all_concepts[1].extend(result[3])
  parents = parent_concept(result[3])
  total = result
  total[3] = parents  

  final_df = pd.DataFrame(columns=['note_id', 'org_text', 'concept', 'parent', 'category'])
  final_df['note_id'] = total[0]
  final_df['org_text'] = total[1]
  final_df['concept'] = total[2]
  final_df['parent'] = total[3]
  final_df['category'] = total[4]
  print(final_df)

  path = r'fill in path' 
  final_df.to_json(path) 

  all_concepts[0].extend(total[2])
  all_concepts[2].extend(total[4])

#get embeddings 
cats = ['disease','drug','procedure']
for c in cats:
  concepts = [[],[]]
  for i in range(len(all_concepts[2])):
    if all_concepts[2][i] == c:
      concepts[0].append(all_concepts[0][i])
      concepts[1].append(all_concepts[1][i])
  get_embedding(vec_umls, concepts, c)