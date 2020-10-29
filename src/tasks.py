import torchvision.transforms as transforms
import torchvision
import json 

import os
import numpy as np
import h5py
import torch
from scipy.misc import imread, imresize
from tqdm import tqdm
from collections import Counter
from random import seed, choice, sample
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from tqdm import tqdm

class COCO_data(Dataset):
    def __init__(self, captions_path, image_path, split, image_size=256):
        
        assert split in {'train','val','test'}

        self.split = split
        self.image_path = image_path
                         
        self.word_to_index = {}
        self.index_to_word = {}
        
        json_file = json.load(open(captions_path,'r'))
        
        captions = json_file['images']
        
        self.captions = []
        
        t_captions = captions.copy()
        for i,row in enumerate(t_captions):
            if split not in row['filepath']:
                captions.remove(t_captions[i])
            else:
                        
                for caption in row['sentences']:
                    caption_dict = {}
                    for key in row:
                        if type(row[key]) != list:
                            caption_dict[key] = row[key]
                    
                    for key in caption:
                        caption_dict[key] = caption[key]
                        
                    self.captions.append(caption_dict)
                           
                    for word in caption['tokens']:
                        if word not in self.word_to_index:
                            curr_len = len(list(self.word_to_index.keys())) + 3
                            self.word_to_index[word] = curr_len
                            self.index_to_word[curr_len] = word
                
                                 
                         
                         
        self.image_size = image_size
        self.transforms = transforms.Compose(
                            [
                                transforms.Resize((self.image_size,self.image_size), interpolation=2),
                                transforms.ToTensor(), 
                                transforms.Lambda(lambda x: x.repeat(3,1,1) if x.shape[0]==1 else x),
                                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                     std=[0.229, 0.224, 0.225]),
                            ]
                        )
        
            
                         
    def __len__(self):
        
         return len(self.captions)
                         
    def reset_indices_dict(self):
        for key in self.caption_indices_dict:
            self.caption_indices_dict[key] = 0
                         
    def __getitem__(self, index):
         
#         print(index)

        caption_dict = self.captions[index]

        image_path = os.path.join(self.image_path,caption_dict['filepath'],caption_dict['filename'])

        image = Image.open(image_path)
        image = self.transforms(image)

        caption = caption_dict['tokens']
#         self.caption_indices_dict[captions['imgid']] += 1
        print(index)
#         print(index,image_path,caption)

        for i in range(len(caption)):
            caption[i] = self.word_to_index[caption[i]]

        return image, caption          
           
def collate_fn(batch):
        
    image_size = batch[0][0].shape[-1]
    images = torch.zeros(len(batch), 3, image_size, image_size)
    
    max_caption_len = 0
    for i in range(len(batch)):
        images[i] = batch[i][0]
        max_caption_len = max(max_caption_len, len(batch[i][1]))
    max_caption_len += 2
                
    captions = torch.zeros(len(batch), max_caption_len)
    lengths = torch.zeros_like(captions)
    
    for i in range(len(batch)):
        curr_len = len(batch[i][1])
        captions[i] = torch.LongTensor([1] + batch[i][1] + [2] + [0]*(max_caption_len - curr_len - 2))
    
    return images, captions, lengths

if __name__ == '__main__':
     
    dataset = COCO_data("../../coco_data/dataset_coco.json","../../coco_data",'train')
    loader = DataLoader(dataset, batch_size=16, shuffle=False, collate_fn=collate_fn, num_workers=4)
    
    with tqdm(total=len(dataset)) as progress_bar:
        for i,instance in enumerate(loader):
            image, caption = instance

            progress_bar.update(len(image)
            
            