# -*- coding: utf8 -*-
##################################################
# kNN algorithm starting from a covariance matrix
#################################################

# NB : still not running properly
# NB2 : now : if a movie from the test dataset is not in the train dataset, 'NA' value is given


import numpy, pandas
import os
import time
import sys
import zipimport
from sklearn.metrics import confusion_matrix
import operator
import math
from sklearn.metrics import mean_squared_error

#maxdate of the previous file
if len(list(sys.argv)) > 1 :
  sigma = float(sys.argv[1])
else :
  sigma =.1
maxDate ="2000-12-31"

###Input files : covariance matrix, list of movies, test data
timestart =  time.time()
#~ print timestart

path = 'C:/Users/Thibault/Desktop/ENSAE/Cours3A/Network Data/download/'
if sys.platform == 'linux2':
	path = '../'
#~ Covin = path+'compressMat_'+maxDate+'.txt'
Covin = path+'compressMat_'+maxDate+'_%f.txt' % sigma
Cov = numpy.loadtxt(Covin, delimiter = ',')
print 'time to import Cov: '+ str((time.time()-timestart)/60)

fin = path+'dbEffects'+maxDate+'_%f.txt' % sigma
df = pandas.read_csv(fin,sep="\t",encoding="utf8")
#~ ftest = path+'database_'+maxDate+'_Test.txt.gz'
#~ ftest = path+'testUsed_'+maxDate+'.txt.gz'
#~ ftest = path+'test'
ftest = path+'db_test_random_10000.txt'
#~ dfTest = pandas.read_csv(ftest,sep=",",encoding="utf8",compression = 'gzip')
dfTest = pandas.read_csv(ftest,sep="\t",encoding="utf8")
#~ print dfTest.shape
#~ dfTest = dfTest.head(10000)
#~ dfTest.to_csv(path+'testUsed_'+maxDate+'.txt',sep=",",encoding="utf8")
#~ dfTest = pandas.read_csv(ftest,sep=",",encoding="utf8")


print 'time to import Cov + Train and Test dataframes: %d min ' % ((time.time()-timestart)/60)

print 'hey ho let s go'
### kNN algorithm from covariance matrix
listMovies = df.groupby('movieID')['movieID'].max().tolist()
DicMovies = {}
index = 0
for el in listMovies :
	DicMovies[el] = index
	index += 1
listUsers = df.groupby('userID')['userID'].max().tolist()
DicUsers = {}
index = 0
for el in listUsers :
	DicUsers[el] = index
	index += 1

def getNeighbors(moviesviewed, movietest, k): #k nearest neighbors among the movies that the user has already seen
    similarities = [] #list of tuples with (movies,similarity with movie)
    i_movieTest = DicMovies[movietest]
    for movie2 in moviesviewed: #moviestrain is the list of movieIDs that the current user has viewed
        if (movie2 != movietest and movietest in DicMovies): #listmovies is the list of movies in the covariance matrix: has to be in it
            similarities.append((movie2, Cov[i_movieTest,DicMovies[movie2]]))
    similarities.sort(key=operator.itemgetter(1), reverse=True)
    n = min(k,len(similarities))
    neighbors = [el[0] for el in similarities[0:n]]
    return neighbors

def getRating(userviewed, neighbors): #we have a list of similar movies, now we have to derive the rating
    #majority vote
    classVotes = {}
    for x in range(len(neighbors)):
        neighbor = neighbors[x] #scalar, it is the movieID of the neighbor
        rating = float(userviewed.ix[:,1][userviewed.ix[:,0]==neighbor]) #scalar
        if rating in classVotes:
            classVotes[rating] += 1
        else:
            classVotes[rating] = 1
        res = 0
        try : #not perfect but I don t see why it is needed...
            res = max(classVotes.iteritems(),key=operator.itemgetter(1))[0] #if I understand correctly you don't have to sort, you just take the max
        except :
            res = 3
        return res

def accuracymeasures(predictions, dataTest):
    #1 remove NA and corresponding lines in dataTest
    idx_remove = []
    predictions2 = []
    targets2 = []
    for x in range(len(predictions)):
        if predictions[x]=='NA':
            idx_remove.append(x)
        else :
            predictions2.append(predictions[x])
            targets2.append(dataTest['rating'].tolist()[x])
    #2 Accuracy measures: RMSE, accuracy percentage and confusion table
    #accuracy
    wellPred = 0
    for k in range(len(predictions2)):
        if predictions2[k] == targets2[k]:
            wellPred +=1
    acc = float(wellPred)/len(targets2)
    rmse = math.sqrt(mean_squared_error(predictions2,targets2))    
    #ROC
    roc = confusion_matrix(targets2, predictions2)  
    print '______________________________'
    print '           Accuracy'
    print 'RMSE = '+str(rmse)
    print 'Accuracy = '+str(100*acc)+'%'
    print ' '
    print 'Confusion matrix:'
    print roc
    print '______________________________'
    return rmse


def kNN(k):
    predictions = []
    for movie in (dfTest['movieID']).unique():
        userlist = dfTest[dfTest['movieID']==movie]['userID'].tolist()
        for user in userlist:
            if movie not in DicMovies : #movie we want to get the neighbors of has to be in the cov matrix
                predictions.append('NA')
                continue
            if user in DicUsers:
                userviewed = df[df['userID']==user][['movieID','rating']]
                moviesviewed = userviewed['movieID'].tolist()
            else :
                userviewed = df.groupby('movieID')[['movieID', 'rating']].agg(['mean'])
                userviewed = numpy.round(userviewed) #we want integer values
                moviesviewed = userviewed['movieID']['mean'].tolist()
            neighbors = getNeighbors(moviesviewed, movie, k) #list of closest movies he has viewed
            result = int(getRating(userviewed, neighbors) ) #rating value
            predictions.append(result)
    return accuracymeasures(predictions,dfTest)
    
def kNNbis(kList):
    predictions = {}
    res = {}
    #~ predictions = []
    for k in kList :
        predictions[k] = []
    for movie in (dfTest['movieID']).unique():
        userlist = dfTest[dfTest['movieID']==movie]['userID'].tolist()
        for user in userlist:
            if movie not in DicMovies : #movie we want to get the neighbors of has to be in the cov matrix
                for k in kList :
                    neighbors = getNeighbors(moviesviewed, movie, k) #list of closest movies he has viewed
                    result = int(getRating(userviewed, neighbors) ) #rating value
                    predictions[k].append(result)
                continue
            if user in DicUsers:
                userviewed = df[df['userID']==user][['movieID','rating']]
                moviesviewed = userviewed['movieID'].tolist()
            else :
                userviewed = df.groupby('movieID')[['movieID', 'rating']].agg(['mean'])
                userviewed = numpy.round(userviewed) #we want integer values
                moviesviewed = userviewed['movieID']['mean'].tolist()
            for k in kList :
                neighbors = getNeighbors(moviesviewed, movie, k) #list of closest movies he has viewed
                result = int(getRating(userviewed, neighbors) ) #rating value
                predictions[k].append(result)
    for k in kList :
        res[k] = accuracymeasures(predictions,dfTest)
    return res
    #~ return accuracymeasures(predictions,dfTest)
#k=3  RMSE=1.0 , acc = 27%
print "Oh yeah baby"
print kNN(20)
#~ res = {}
#~ for k in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 19, 20, 21, 25, 30] :
	#~ print k
	#~ res[k] = kNN(k)
#~ import json
#~ json.dumps(res)
print "Computation time: %f min"%((time.time()-timestart)/60)
