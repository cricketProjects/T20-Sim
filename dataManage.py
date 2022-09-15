import pickle

dat = open('extractedData/allDataAdjusted', 'rb')
playersData = pickle.load(dat)
dat.close()

dat = open('extractedData/allPlayersName', 'rb')
playersName = pickle.load(dat)
dat.close()