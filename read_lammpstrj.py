#modified Chris Liepold's program by Alex Smith in July 2016

#Usage:
#Can be used as an import into other programs or called straight through the command line
#call from command line with python (file to convert) (optional output file name)
#if not output file name is specified then it will get rid of the last 4 characters of the inputted 
#file name and then add a .tr
#if it ends up being too slow: consider using numpy tofile and fromfile if it starts to get too slow for the input sizes

import sys
import numpy as np

#Takes in a string and returns whether or not it's something that marks that it's a
def isNewStep(line):
    return len(line) < 1 or line[0] == 'I' or len(line.split()) == 1 or len(line.split()) != 5

#Takes in a line (a valid time step as a string) and returns the x,y,z values which
# are located in line[1],line[2], line[3] (n.b. python slices are half open intervals 
#[1,4) -> so a = [0,1,2,3,4] then a[1:4] = [1,2,3])
def parseLine(line): 
    return map(float, line.split()[2:5])

#Takes in a string of the path to the file, and returns a 2D array of the timesteps as 
#a track file
def convertToTrackFile(f):
    #start at -1 to have 0 - based indexing
    atomNumber = -1
    frameNumber = -1
    output = []
    for line in open(f):
        if isNewStep(line):
            atomNumber = -1
            frameNumber += 0.1 # do this because there are nine new frame lines between
            #each time step
            continue #there are no atoms to add in this line, so keep looping

        atomNumber += 1
        (x,y,z) = parseLine(line)
        output.append([x,y,z,int(frameNumber+1.0), atomNumber])
    return output

#only run this part if it's called from command line (so this can be imported into other programs)
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Specify the input and (optional) output file"
        exit(1)
    f = sys.argv[1]
    if len(sys.argv) == 2:
        if len(f) >= 5:
            outname = f[:-4] + '.tr'
        else:
            outname = f + '.tr'
    else:
        outname = sys.argv[2]
    outarr = convertToTrackFile(f)
    np.savetxt(outname,outarr,fmt = ['%3.5e','%3.5e','%3.5e','%1i','%1i'])
