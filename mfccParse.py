from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as ms
ms.use('seaborn-muted')

import IPython.display
import librosa
import librosa.display

import os
import pickle

# TODO:
# Load wav file
# Get MFCC Output
# Slice into appropriate chunks
# Save for training


x_train = []
y_train = []
x_test = []
y_test = []


def parseAudio(genreIndex, songIndex, fName):
	y, sr = librosa.load(fName)
	# CHANGE HERE
	audioLength = 60*sr

	if y.shape[0] > audioLength:
		extraLength = int((y.shape[0] - audioLength)/2)
		y = y[extraLength : audioLength + extraLength]
	else:
		audioLength = y.shape[0]
	
	logam = librosa.logamplitude
	melgram = librosa.feature.melspectrogram
	longgrid = logam(melgram(y=y, sr=44100,n_fft=1024, n_mels=128),ref_power=1.0)
	longgrid = np.expand_dims(longgrid, axis=3)
	# chunks = map(lambda col: [col[x:x+128] for x in range(0, len(col)-128, 128)], longgrid)
	chunks = [longgrid[:, x:x+128] for x in range(0, len(longgrid[0])-128,128)]
	chunks = np.asarray(chunks)
	# print(chunks.shape)

	oneLabel = [0]*10
	oneLabel[genreIndex] = 1

	[x_train.append(x) for x in chunks[:15]]
	[y_train.append(x) for x in [oneLabel]*15]
	[x_test.append(x) for x in chunks[15:]]
	[y_test.append(x) for x in [oneLabel]*(len(chunks)-15)]
	print(fName)
	print('x_train: ', len(x_train), len(x_train[0]), len(x_train[0][0]))
	print('y_train: ', len(y_train))
	print('x_test: ', len(x_test), len(x_test[0]), len(x_test[0][0]))
	print('y_test: ', len(y_test))


#parseAudio(0,0,'stupid cupid.wav')
gid = 0
for root, dirs, files in os.walk('Homemade Dataset'):
	if '_pickle' not in root and '_img' not in root and 'Dataset' not in root:
		sid = 0
		for name in files:
			if 'wav' in name:
				parseAudio(gid, sid, root + '/' + name)
				sid +=1
		gid +=1

x_train = np.asarray(x_train)
y_train = np.asarray(y_train)
x_test = np.asarray(x_test)
y_test = np.asarray(y_test)


pickel.dump(x_train, open('x_train_mel.p', 'wb'))
pickel.dump(y_train, open('x_train_mel.p', 'wb'))
pickel.dump(x_test, open('x_test_mel.p', 'wb'))
pickel.dump(y_test, open('y_test_mel.p', 'wb'))