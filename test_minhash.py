from minhash import computeUniSet, createCharacterMatrix, createHashfunctions, createShingleBag, findPrimeAbove, shingleDocuments, minhash, LSH, jaccSim, sigSim
import random

def test_shingleBag():
    document = "I will make you an offer you can't refuse"
    shingleBag = createShingleBag(document, 3)
    expectedBag = [
        "make offer can't ",
        "offer can't refuse "
    ]
    assert shingleBag == expectedBag

def test_shingleDocuments():
    documents = [
        "I will make you an offer you can't refuse",
        "The dog ate the cat and went home"
    ]
    shingledDocs = shingleDocuments(documents, 3)
    expectedShingles = {
        0: ["make offer can't ", "offer can't refuse "],
        1: ["dog ate cat ", "ate cat went ", "cat went home "]
    }
    assert shingledDocs == expectedShingles

def test_uniSet():
    documents = [
        "I will make you an offer you can't refuse",
        "The dog ate the cat and went home",
        "I will make you an offer",
        "The dog ate the cat"
    ]
    shingledDocs = shingleDocuments(documents, 3)
    uniSet = computeUniSet(shingledDocs)
    expectedUniSet = [
        "make offer can't ",
        "offer can't refuse ",
        "dog ate cat ",
        "ate cat went ",
        "cat went home "
    ]
    assert uniSet == expectedUniSet

def test_charMatrix():
    documents = [
        "I will make you an offer you can't refuse",
        "The dog ate the cat and went home",
        "I will make you an offer",
        "The dog ate the cat"
    ]
    charMatrix = createCharacterMatrix(documents, 3)
    expectedMatrix = [
                        [1,1,0,0,0], # 0
                        [0,0,1,1,1], # 1
                        [0,0,0,0,0], # 2
                        [0,0,1,0,0]  # 3
                    ]
    assert charMatrix == expectedMatrix

def test_findPrime():
    assert findPrimeAbove(0) == 1
    assert findPrimeAbove(1) == 2
    assert findPrimeAbove(2) == 3
    assert findPrimeAbove(3) == 5
    assert findPrimeAbove(5) == 7
    assert findPrimeAbove(7) == 11
    assert findPrimeAbove(11) == 13
    assert findPrimeAbove(13) == 17
    assert findPrimeAbove(17) == 19
    assert findPrimeAbove(19) == 23
    assert findPrimeAbove(23) == 29

def test_createHashfunctions():
    randomValues = [random.randint(0,10000) for i in range(100)]
    j=0
    for maxValue in randomValues:
        prime = findPrimeAbove(maxValue)
        hashFunctions = createHashfunctions(10,maxValue)
        for hashFunction in hashFunctions:
            print(j)
            randNumber = random.randint(0,100000)
            assert hashFunction(randNumber)<prime
            j+=1

def test_minhash():
    hashFunctions = [lambda x: (x+1)%5, lambda x: (3*x+1)%5,]
    charMatrix = [
                    [1,0,0,1,0], # 0
                    [0,0,1,0,0], # 1
                    [0,1,0,1,1], # 2
                    [1,0,1,1,0]  # 3
                ]
    sigMatrix = minhash(charMatrix, hashFunctions)
    expectedMatrix = [
        [1,0],
        [3,2],
        [0,0],
        [1,0]
    ]
    assert sigMatrix == expectedMatrix

def test_LSH():
    sigMatrix = [
                    [1,3,0,1,1,1], # 0
                    [0,2,1,2,2,2], # 1
                    [0,1,3,3,3,3], # 2
                    [0,2,1,2,2,2], # 3
                    [2,2,1,2,2,2], # 4
                    [0,1,3,1,1,1], # 5
                    [0,2,1,1,1,1], # 6
                    [2,2,1,0,0,0]  # 7
                ]
    candidates = LSH(sigMatrix, 2, 3)
    # check first band for candidates
    assert list(candidates[0].values())[0] == [1,3,6]
    assert list(candidates[0].values())[1] == [2,5]
    assert list(candidates[0].values())[2] == [4,7]
    # check second band for candidates
    assert list(candidates[1].values())[0] == [0,5,6]
    assert list(candidates[1].values())[1] == [1,3,4]

def test_jaccSim():
    charMatrix = [
                    [1,0,0,1,0], # 1
                    [0,0,1,0,0], # 2
                    [0,1,0,1,1], # 3
                    [1,0,1,1,0]  # 4
                ]
    assert jaccSim(charMatrix,0,0) == 1
    assert jaccSim(charMatrix,0,1) == 0
    assert jaccSim(charMatrix,0,2) == 1/4
    assert jaccSim(charMatrix,0,3) == 2/3
    assert jaccSim(charMatrix,1,1) == 1
    assert jaccSim(charMatrix,1,2) == 0
    assert jaccSim(charMatrix,1,3) == 1/3
    assert jaccSim(charMatrix,2,2) == 1
    assert jaccSim(charMatrix,2,3) == 1/5
    assert jaccSim(charMatrix,3,3) == 1

def test_sigSim():
    sigMatrix = [
                    [1,3,0,1,1,1], # 0
                    [0,2,1,2,2,2], # 1
                    [0,1,3,3,3,3], # 2
                    [0,2,1,2,2,2], # 3
                    [2,2,1,2,2,2], # 4
                    [0,1,3,1,1,1], # 5
                    [0,2,1,1,1,1], # 6
                    [2,2,1,0,0,0]  # 7
                ]
    assert sigSim(sigMatrix,0,0) == 1
    assert sigSim(sigMatrix,0,1) == 0
    assert sigSim(sigMatrix,0,2) == 0
    assert sigSim(sigMatrix,0,5) == 3/6
    assert sigSim(sigMatrix,0,6) == 3/6
    assert sigSim(sigMatrix,0,7) == 0
    assert sigSim(sigMatrix,1,3) == 1
    assert sigSim(sigMatrix,1,6) == 3/6
    assert sigSim(sigMatrix,4,7) == 3/6
    assert sigSim(sigMatrix,6,7) == 2/6
