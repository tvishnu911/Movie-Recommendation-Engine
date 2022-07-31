import numpy as np 
import pandas as pd
from web.models import Myrating
import scipy.optimize 


def Myrecommend():
	def normalizeRatings(myY, myR):
    	
		Ymean = np.sum(myY,axis=1)/np.sum(myR,axis=1)
		Ymean = Ymean.reshape((Ymean.shape[0],1))
		return myY-Ymean, Ymean
	
	def flattenParams(myX, myTheta):
		return np.concatenate((myX.flatten(),myTheta.flatten()))
    
	def reshapeParams(flattened_XandTheta, mynm, mynu, mynf):
		assert flattened_XandTheta.shape[0] == int(mynm*mynf+mynu*mynf)
		reX = flattened_XandTheta[:int(mynm*mynf)].reshape((mynm,mynf))
		reTheta = flattened_XandTheta[int(mynm*mynf):].reshape((mynu,mynf))
		return reX, reTheta

	def cofiCostFunc(myparams, myY, myR, mynu, mynm, mynf, mylambda = 0.):
		myX, myTheta = reshapeParams(myparams, mynm, mynu, mynf)
		term1 = myX.dot(myTheta.T)
		term1 = np.multiply(term1,myR)
		cost = 0.5 * np.sum(np.square(term1-myY))
    	
		cost += (mylambda/2.) * np.sum(np.square(myTheta)) 
		cost += (mylambda/2.) * np.sum(np.square(myX))
		return cost

	def cofiGrad(myparams, myY, myR, mynu, mynm, mynf, mylambda = 0.):
		myX, myTheta = reshapeParams(myparams, mynm, mynu, mynf)
		term1 = myX.dot(myTheta.T)
		term1 = np.multiply(term1,myR)
		term1 -= myY
		Xgrad = term1.dot(myTheta)
		Thetagrad = term1.T.dot(myX)
    	
		Xgrad += mylambda * myX 
		Thetagrad += mylambda * myTheta
		return flattenParams(Xgrad, Thetagrad)

	df=pd.DataFrame(list(Myrating.objects.all().values()))
	print(df)
	mynu=df.user_id.unique().shape[0]
	mynm=df.movie_id.unique().shape[0]
	mynf=10
	Y=np.zeros((mynm,mynu))
	for row in df.itertuples():
		print(row)
		Y[row[2]-1, row[4]-1] = row[3]
	R=np.zeros((mynm,mynu))
	for i in range(Y.shape[0]):
		for j in range(Y.shape[1]):
			if Y[i][j]!=0:
				R[i][j]=1

	Ynorm, Ymean = normalizeRatings(Y,R)
	X = np.random.rand(mynm,mynf)
	Theta = np.random.rand(mynu,mynf)
	myflat = flattenParams(X, Theta)
	mylambda = 12.2
	result = scipy.optimize.fmin_cg(cofiCostFunc,x0=myflat,fprime=cofiGrad,args=(Y,R,mynu,mynm,mynf,mylambda),maxiter=40,disp=True,full_output=True)
	resX, resTheta = reshapeParams(result[0], mynm, mynu, mynf)
	prediction_matrix = resX.dot(resTheta.T)
	return prediction_matrix,Ymean
	







