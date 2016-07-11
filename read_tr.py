import numpy as np
# from mpl_toolkits.mplot3d import Axes3D
# from scipy import loadtxt, optimize, constants
# from scipy.optimize import curve_fit
# from scipy.odr import *
# import matplotlib.pyplot as plt
# import random as random
# from Sites import generate_seed, plot_sphere, balance_points
import math
# import fileinput
import os
import re
from StringIO import StringIO

def read_tr(fname,outname):
	print fname
	num_lines = sum(1 for line in open(fname))

	with open(fname, 'r') as f:
		x = f.tell()
		nAtoms = int(f.readline())
		f.seek(x)
		# nAtoms = 16
		nframes = num_lines / (nAtoms + 2)
		outarr = np.zeros((nAtoms * nframes, 5))
		for i in range(0,num_lines):
			if i % (num_lines / 100) == 0:
				print int((100. * i) / num_lines)
			line = f.readline()
			atomNumber = (i % (nAtoms + 2)) - 2
			frameNumber = (i - atomNumber - 2) / (nAtoms + 2)
			if atomNumber > -1:
				x,y,z = np.genfromtxt(StringIO(line),usecols=(1,2,3),unpack = True)
				index = frameNumber * nAtoms + atomNumber
				outarr[index,0:3] = [x,y,z]
				outarr[index,3] = frameNumber
				outarr[index,4] = atomNumber
	print "Loaded all lines"
	np.savetxt(outname,outarr,fmt = ['%3.5e','%3.5e','%3.5e','%1i','%1i'])
	return outarr
		# savetxt("out.tsv",outarr)
			# print i
	# print nAtoms
	# print num_lines
	# for line in open(fname):
	# 	linetxt = readline()
	
	# for i in range(1,nframes + 1):
	# 	out = np.genfromtxt(fname,max_rows = nAtoms, skip_header = ((i - 1) * (2 + nAtoms) + 2))
	# 	print np.shape(out)
	# 	print i
	# print nAtoms
	# print num_lines
	# print num_lines / (nAtoms +2)


read_tr("dump2.xyz","dump2.tr")

# np.savetxt("dump2.tr",read_tr("dump2.xyz"))