import pandas as pd
from nltk.corpus import stopwords
import random
import sys
from datasketch import MinHash

global stopWords
global maxRow

stopWords = set(stopwords.words('english'))

def loadData(csvPath):
    with open(csvPath, newline='', encoding="utf-8") as csvFile:
        colList = ["transcription"]
        documents = pd.read_csv(csvFile, usecols=colList)
        #print("type = "+str(type(documents["transcription"])))
        return documents["transcription"]

def createShingleBag(document, shingleSize):
    """ preprocessing """
    # remove punctuation and reduce white space to one blank
    document = str(document).replace(",","")
    document = str(document).replace(".","")
    document = str(document).replace(";","")
    document = str(document).replace(":","")
    document = ' '.join(document.split()).lower()
    # split into words
    words = document.split(" ")
    # remove stop words
    filteredWords = [w for w in words if not w.lower() in stopWords]
    """ shingling """
    shingleBag = []
    #print(len(filteredWords)-shingleSize)
    for i in range(len(filteredWords)-shingleSize+1):
        currentShingle = ""
        # append k-1 words to get the shingle
        for j in range(shingleSize):
            currentShingle += filteredWords[i+j]+" "
        # add shingle to bag of shingles
        shingleBag.append(currentShingle)
    return shingleBag

def shingleDocuments(documents, shingleSize):
    shingledDocuments = {}
    currentIndex=0
    for document in documents:
        currentBag = createShingleBag(document,shingleSize)
        shingledDocuments[currentIndex] = currentBag
        currentIndex+=1
    return shingledDocuments

def computeUniSet(shingledDocuments):
    uniSet = []
    for document in shingledDocuments.values():
        for shingle in document:
            # only add if shingle does not exist yet
            if not shingle in uniSet:
                uniSet.append(shingle)
    return uniSet

def createCharacterMatrix(documents, shingleSize):
    shingledDocuments = shingleDocuments(documents,shingleSize)
    uniSet = computeUniSet(shingledDocuments)
    characterMatrix = [None] * len(documents)
    for i in range(len(documents)):
        characterVector = []
        currentBag = createShingleBag(documents[i],shingleSize)
        for element in uniSet:
            if element in currentBag:
                characterVector.append(1)
            else:
                characterVector.append(0)
        characterMatrix[i] = characterVector
    return characterMatrix

# taken from https://stackoverflow.com/questions/69502775/python-program-to-find-5-prime-numbers-above-and-below-a-given-integer
def findPrimeAbove(n):
    num = n+1
    while True:
        for i in range(2, num-1):
            if num % i == 0:
                break
        else:
            return num
        num += 1

def createHashfunctions(hashCount, maxValue):
    prime = findPrimeAbove(maxValue)
    hashFunctions = []
    valuePairs = []
    for i in range(hashCount):
        a = random.randint(0, maxValue)
        b = random.randint(0, maxValue)
        # make sure every hash function is unique
        while [a,b] in valuePairs:
            a = random.randint(0, maxValue)
            b = random.randint(0, maxValue)
        valuePairs.append([a,b])
        #print(str(a)+", "+str(b)+", "+str(prime))
        hashFunctions.append(lambda x: (a*x+b) % prime)
    return hashFunctions


# unfortunately this self implemented function is not working :/
'''
def minhash(charMatrix, hashFunctions):
    # fill signature matrix with "infinity"
    signatureMatrix = [
        [ sys.maxsize for x in range(len(hashFunctions))] 
        for y in range(len(charMatrix))
    ]
    # compute values for signature matrix
    for c in range(len(charMatrix)):
        for r in range(len(charMatrix[c])):
            if charMatrix[c][r] == 1:
                for i in range(len(hashFunctions)):
                    hashValue = hashFunctions[i](r)
                    signatureMatrix[c][i] = min(signatureMatrix[c][i], hashValue)
    return signatureMatrix
'''

def minhash(shingleBagOne, shingleBagTwo, hashCount):
    hashOne = MinHash(num_perm=hashCount)
    hashTwo = MinHash(num_perm=hashCount)
    for shingle in shingleBagOne:
        hashOne.update(shingle.encode("utf8"))
    for shingle in shingleBagTwo:
        hashTwo.update(shingle.encode("utf8"))
    return hashOne.jaccard(hashTwo)

def LSH(sigMatrix, bandCount, rowCount):
    # banding technique
    rowTotal = 0
    bandHashes = []
    for b in range(bandCount):
        bandHashes.append({})
        for c in range(len(sigMatrix)):
            rowString = ""
            for r in range(rowCount):
                rowString += str(sigMatrix[c][rowTotal+r])+","
            hashValue = hash(rowString)
            #print("hashValue: "+str(hashValue)+", keyList: "+str(list(bandHashes[b].keys())))
            print("b = "+str(b))
            if hashValue in bandHashes[b].keys():
                print("hashValue is in key list")
                bandHashes[b][hashValue].append(c)
            else:
                print("hashValue is NOT in key list")
                bandHashes[b][hashValue] = [c]
            print("-----------------------")
        rowTotal += rowCount

    # remove band entries with one element only
    candidates = []
    for b in range(bandCount):
        candidates.append({})
        for hashValue in bandHashes[b].keys():
            if len(bandHashes[b][hashValue]) > 1:
                candidates[b][hashValue] = bandHashes[b][hashValue]
    return candidates

def jaccSim(charMatrix, c1, c2):
    intersectionCounter = 0
    unionCounter = 0
    for r in range(len(charMatrix[0])):
        if (charMatrix[c1][r] == 1) or (charMatrix[c2][r] == 1):
            unionCounter += 1
        if (charMatrix[c1][r] == 1) and (charMatrix[c2][r] == 1):
            intersectionCounter += 1
    return (intersectionCounter/unionCounter)

def sigSim(sigMatrix, c1, c2):
    matchCounter = 0
    total = 0
    for r in range(len(sigMatrix[0])):
        if (sigMatrix[c1][r] == sigMatrix[c2][r]):
            matchCounter += 1
        total += 1
    return (matchCounter/total)