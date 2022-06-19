import pandas as pd
import streamlit as st
from datasketch import MinHash
from minhash import minhash, createShingleBag, loadData


docCountLimit = 1000
documents = loadData("./mtsamples.csv")[0:docCountLimit]

st.write("## Shingling")

docCount = st.slider('Number of documents', value=500, step=100, min_value=100, max_value=len(documents))
shingleSize = st.slider('Shingle size', value=5, min_value=1, max_value=15)

shortDocuments = [str(doc)[0:50]+"..." for doc in documents[0:docCount]]

bagOne = st.selectbox("Select bag 1:", shortDocuments, index=0)
bagTwo = st.selectbox("Select bag 2:", shortDocuments, index=0)

if bagOne == bagTwo:
    st.write("#### Please select two different bags!")
else:
    # create shingle bags of selected documents
    shingleBagOne = createShingleBag(documents[shortDocuments.index(bagOne)],shingleSize)
    shingleBagTwo = createShingleBag(documents[shortDocuments.index(bagTwo)],shingleSize)
    # show shingle bags as table
    with st.expander("Expand to show shingles..."):
        st.table(pd.DataFrame([shingleBagOne,shingleBagTwo], index=(bagOne,bagTwo)).transpose())
    # select number of permutations being used
    st.write("## Locality-Sensitive Hashing")
    hashCount = st.slider('Number of hash functions', value=500, step=100, min_value=100, max_value=500)
    # compute LSH estimation and actuall similarity
    if st.button("Run"):
        st.write("### LSH Estimation")
        st.write("LSH estimation for "+str(hashCount)+": ", minhash(shingleBagOne, shingleBagTwo, hashCount))
        st.write("### Jaccard Similarity")
        setOne = set(shingleBagOne)
        setTwo = set(shingleBagTwo)
        actual_jaccard = float(len(setOne.intersection(setTwo)))/float(len(setOne.union(setTwo)))
        st.write("Actual Jaccard Similarity is", actual_jaccard)