"""Print pairwise cosine similarity for embedding sanity checking."""
from __future__ import annotations
import math
from src.config import get_settings
from src.retrieval.vector_store import embeddings

def cosine(a,b):
    dot=sum(x*y for x,y in zip(a,b))
    na=math.sqrt(sum(x*x for x in a)); nb=math.sqrt(sum(y*y for y in b))
    return dot/(na*nb)

def main():
    s=get_settings(); e=embeddings(s)
    texts=["The purifier makes three short beeps when the sediment filter is saturated.",
           "Three brief audible alarms indicate that the sediment pre-filter has reached saturation.",
           "The customer may request a return within fourteen calendar days of delivery."]
    vectors=e.embed_documents(texts)
    for i in range(len(texts)):
        for j in range(i+1,len(texts)):
            print(i,j,round(cosine(vectors[i],vectors[j]),4))
if __name__=="__main__": main()
