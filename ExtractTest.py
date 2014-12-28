import os
import time
import sys
liDates = []
"""if len(list(sys.argv)) > 1 :
    liDates = sys.argv[1:]
else :
    liDates = ["2000-0631"]
"""
liDates = ["2001-03-31"]
liDatesLi = [ el.split('-') for el in liDates]
liDatesLiNum = [map(int,el) for el in liDatesLi]
liDatesTrain =     ["2000-12-31"]
liDatesLiTrain = [ el.split('-') for el in liDatesTrain]
liDatesLiNumTrain = [map(int,el) for el in liDatesLiTrain]


start_path = 'C:/Users/Thibault/Desktop/ENSAE/Cours3A/Network Data/download/'
if sys.platform == 'linux2':
    start_path = '../'

path = start_path + 'training_set/'
nameDir = {}
for maxDate in liDates :
    nameDir[maxDate] = start_path+ 'testing_' + maxDate
    if not(os.path.exists(nameDir[maxDate] )):
        os.mkdir(nameDir[maxDate] )

def isDateGreater_aux(li0,li1) :
    if li0 == [] :
        return True
    el0 = li0[0]
    el1 = li1[0]
    if el0> el1:
        return False
    if el0< el1 :
        return True
    return isDateGreater_aux(li0[1:],li1[1:])




if __name__ == "__main__" :
    for filename in os.listdir(path) :
        fin = open('/'.join([path,filename]),'r')
        fin.readline()
        resDic = {}
        for line in fin :
            parsed = line.split(',')
            currDateStr = parsed[-1].replace('\r','').replace('\n','')
            liRevDate = map(int,currDateStr.split('-'))
            i = 0
            for maxDateLi in liDatesLi :
                if (isDateGreater_aux(liRevDate,liDatesLiNum[i]) and isDateGreater_aux(liDatesLiNumTrain[i],liRevDate)):
                    if not liDates[i] in resDic :
                        resDic[ liDates[i] ] = open(nameDir[liDates[i]]+'/'+filename,'w')
                    resDic[liDates[i]].write(line)
                i += 1
        fin.close()

        for maxDate in resDic :
                resDic[maxDate].close()
