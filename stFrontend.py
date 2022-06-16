import streamlit as st
from minhash import createCharacterMatrix, createHashfunctions, minhash, shingleDocuments, createShingleBag, loadData, LSH, sigSim, jaccSim
import pandas as pd

docCountLimit = 100
docLengthLimit = 1000
documents = loadData("./mtsamples.csv")[0:docCountLimit]

st.markdown("## Shingling")

docCount = st.slider('Number of documents', value=50, step=5, min_value=5, max_value=len(documents))
docLength = st.slider('Length of documents', value=3000, step=100, min_value=1000, max_value=5000)
shingleSize = st.slider('Shingle size', value=5, min_value=1, max_value=15)

shortDocuments = [str(doc)[0:50]+"..." for doc in documents[0:docCount]]

bagOne = st.selectbox("Select bag 1:", shortDocuments, index=0)
bagTwo = st.selectbox("Select bag 2:", shortDocuments, index=0)

if bagOne == bagTwo:
    st.write("Please select two different bags.")
else:
    shingleBagOne = createShingleBag(documents[shortDocuments.index(bagOne)][0:docLength],shingleSize)
    shingleBagTwo = createShingleBag(documents[shortDocuments.index(bagTwo)][0:docLength],shingleSize)
    with st.expander("Expand to show shingles..."):
        st.table(pd.DataFrame([shingleBagOne,shingleBagTwo], index=(bagOne,bagTwo)).transpose())

st.markdown("## LSH & Jaccard Similarity")

hashCount = st.slider('Number of hash functions', value=100, step=10, min_value=10, max_value=500)

if st.button("Run"):
    st.markdown("### Jaccard Similarity")
    st.write("Computing character matrix...")
    charMatrix = createCharacterMatrix(documents[0:docCount],shingleSize)
    realSim = jaccSim(charMatrix, shortDocuments.index(bagOne), shortDocuments.index(bagTwo))
    st.write("Jaccard similarity: "+str(realSim))
    st.markdown("### Locality-Sensitive Hashing")
    st.write("Computing signature matrix...")
    hashFunctions = createHashfunctions(hashCount,len(charMatrix[0]))
    sigMatrix = minhash(charMatrix,hashFunctions)
    df = pd.DataFrame(sigMatrix)
    st.write(df)
    lshSim = sigSim(sigMatrix, shortDocuments.index(bagOne), shortDocuments.index(bagTwo))
    st.write("LSH estimation: "+str(lshSim))