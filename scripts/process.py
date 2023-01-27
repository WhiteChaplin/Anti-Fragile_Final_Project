# import packages 
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
import random
import os
import pickle
import numpy as np
import pandas as pd

# torch 
import torch
from torch import nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import gluonnlp as nlp
import numpy as np
import pandas as pd

#KoBERT
from kobert.utils import get_tokenizer
from kobert.pytorch_kobert import get_pytorch_kobert_model

#transformer
from transformers import AdamW
from transformers.optimization import get_cosine_schedule_with_warmup

#GPU 설정
device = torch.device("cuda:0")

seed = 77
def seed_everything(seed):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True

# labelEncoder
le = LabelEncoder()
target = pd.read_csv('static\models\DATA_04_target.csv.csv')
le.fit_transform(np.array(target['감정']))

# scaler 
scaler = MinMaxScaler()

#bertmodel의 vocabulary
bertmodel, vocab = get_pytorch_kobert_model()
tokenizer = get_tokenizer()
tok = nlp.data.BERTSPTokenizer(tokenizer, vocab, lower=False)

class BERTDataset(Dataset):
    def __init__(self, dataset, sent_idx, label_idx, bert_tokenizer, max_len,
                 pad, pair):
        transform = nlp.data.BERTSentenceTransform(
            bert_tokenizer, max_seq_length=max_len, pad=pad, pair=pair)
        self.sentences = [transform([i[sent_idx]]) for i in dataset]
        self.labels = [np.int32(i[label_idx]) for i in dataset]

    def __getitem__(self, i):
        return (self.sentences[i] + (self.labels[i], ))

    def __len__(self):
        return (len(self.labels))


class BERTClassifier(nn.Module):
    def __init__(self,
                 bert,
                 hidden_size = 768,
                 num_classes=8,
                 dr_rate=None,
                 params=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate
                 
        self.classifier = nn.Linear(hidden_size , num_classes)
        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)
    
    def gen_attention_mask(self, token_ids, valid_length):
        attention_mask = torch.zeros_like(token_ids)
        for i, v in enumerate(valid_length):
            attention_mask[i][:v] = 1
        return attention_mask.float()

    def forward(self, token_ids, valid_length, segment_ids):
        attention_mask = self.gen_attention_mask(token_ids, valid_length)
        _, pooler = self.bert(input_ids = token_ids, token_type_ids = segment_ids.long(), attention_mask = attention_mask.float().to(token_ids.device))
        if self.dr_rate:
            out = self.dropout(pooler)
        return self.classifier(out)

# device check 
device = torch.device("cuda:0")
print(device)
print("-------------------------------------------")
print("cuda check > ", torch.cuda.is_available())
# -------------------------------------------------


# classifier load
model = BERTClassifier(bertmodel,  dr_rate=0.5).to(device)
print("#### succesffully loaded classifier")
print(" ")


# print("### successfully completed model loading! ")
def run():
    model = pickle.load(open(r'C:\djangoproject\kobert\serve\static\models\data04_model_kobert64.pkl', 'rb'))
    return model 

# process 
def getRank(pred_arr):
  scaled = scaler.fit_transform(pred_arr.reshape(-1,1))
  total = scaled.sum()
  percent = [ (obj/total)*100 for obj in scaled]
  percent = [ i[0] for i in percent]

  main_senti = np.argmax(scaled)
  scaled[main_senti] = 0 
  sub_senti = np.argmax(scaled)

  return le.inverse_transform([main_senti, sub_senti]), percent 

def predictSenti(predict_sentence):
    data = [[predict_sentence, '0']]
    dt = BERTDataset(data, 0, 1, tok, 64, True, False)
    dl = torch.utils.data.DataLoader(dt, batch_size=64, num_workers=5)
    # eval mode 
    
    model.eval()
    
    for token_ids, valid_length, segment_ids, _ in dl:
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)
        pred = model(token_ids, valid_length, segment_ids)   
    return getRank(pred.to('cpu').detach().numpy())