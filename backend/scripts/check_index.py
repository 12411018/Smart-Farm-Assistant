import os, pickle, faiss
faiss_path = os.path.join(os.path.dirname(__file__), '..', 'faiss_store', 'faiss.index')
faiss_path = os.path.abspath(faiss_path)
meta_path = os.path.join(os.path.dirname(__file__), '..', 'faiss_store', 'metadata.pkl')
meta_path = os.path.abspath(meta_path)
print('faiss_path', faiss_path)
print('meta_path', meta_path)
print('faiss exists', os.path.exists(faiss_path))
print('meta exists', os.path.exists(meta_path))
if os.path.exists(meta_path):
    meta = pickle.load(open(meta_path,'rb'))
    print('meta_len', len(meta))
if os.path.exists(faiss_path):
    idx = faiss.read_index(faiss_path)
    print('index_ntotal', idx.ntotal)
