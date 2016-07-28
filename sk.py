import numpy
from scipy import fftpack
import pylab as py
#Created by: Alex Smith
#The input file for this program is a track file (can be made from a .xyz (like from lammps) using the read_tr.py program)
#useful for quick debugging
f = "/Users/alexsmith/Binhua Lab/photos/DataAnalysis/useThisShortDumpToTest.xyz"


#Takes in a list of 2D list's and the scaling factor
def scale(list, factor):
    return [[x*factor,y*factor] for [x,y] in list]

#it is assumed that parseLine will only be called on a particle line,
#so that the line will be of the form: (Particle number) (x) (y) (z) (other stuff)
def parseLine(line):
    return map(float, line.split()[0:2])

#the time step is the 4th field, so the third index position
def isNewStep(line, currentStep):
    return len(line) < 1 or float(currentStep) != float((line.split()[3]))

def maxX(l):
    m = 0
    for i in l:
        if i[0] > m:
            m = i[0]
    return m

def maxY(l):
    m = 0
    for i in l:
        if i[1] > m:
            m = i[1]
    return m

#creates a generator for all of the time steps in the file
#can iterate over it:
#gen = getTimeStep(file)
#steps = []
#for t in gen:
#   steps.append(t)
#to get the first one:
#first = gen.next()
def getTimeStep(fileName):
    f = open(fileName)
    #the first line of a track file is always a valid line
    nextLine = f.readline() 
    points = []
    points.append(nextLine)
    #nextLine is "" on EOF
    currentTimestep = 0
    while nextLine != "":
        nextLine = f.readline()
        if isNewStep(nextLine, currentTimestep):
            #we've reached the start of a new timestep
            if points == []:
                continue
            else:
                yield points
                points = []
                currentTimestep += 1
        else:
            #print nextLine
            point = parseLine(nextLine)
            points.append(point)

#this represents the particles on the screen
def makeImage(timeStep):
    mX = maxX(timeStep) + 2
    mY = maxY(timeStep) + 2
    totalMax = max(mX, mY) + 2
    im = numpy.zeros((totalMax, totalMax))
    for point in timeStep:
        im[round(point[0]),round(point[1])] = 1
    return im

#Go from .xyz to a representation of the particles on the screen as pixels
#then, take the fft of that, multiply by the conjugate (at which point it is real)
#That should be s(k)
def runSK(timeStep):
    im = makeImage(timeStep)
    skTemp = numpy.fft.ifft2(im)
    #usually have to scale this by *10 to get it to look good
    return numpy.fft.fftshift(numpy.abs(skTemp)**2) 
#when combinining the results from runs that have different pixel lengths
#(ex. if you're changing the box size) you will probably want to have some sort of
#padding in order to make them all have the same size when outputted
#(you would do this in the for loop)

#This computes the s(k) average (equivalent to integrating over rings)
#takes in an sk image (an array that has been returned by something like runSK)
def skAverage(skPicture):
    #from the IDL program by BianXiao Cui
    #make these be something that can be inputted
    diameter = 2.56
    ratio = 2.56/12 #micro meter / pixel
    #assuming that the input is already centered
    #(fft shift has been called)
    centerX = len(skPicture) / 2.0
    centerY = len(skPicture[0]) / 2.0
    maxDistance = int(round((numpy.sqrt(len(skPicture)**2 + len(skPicture[0])**2))/2.0))
    #the diagonal length /2 because we are interested in the distance from the center
    yAxis = numpy.zeros(maxDistance + 1)
    yAxisScale = numpy.zeros(maxDistance + 1) # has length of maxDistance to correspond to the x-Axis it's associated with 
    xAxis = numpy.array([x*2*numpy.pi/ratio/len(skPicture) for x in range(maxDistance + 1)])
    #the sort of confusing thing is so that the scale of the xAxis corresponds to real units
    jRange = len(skPicture[0]) #for caching (does python memory alias?)
    #anyway, can do this because each element of skPicture has the same length
    for i in range(len(skPicture)):
        for j in range(jRange):
            distance = round(numpy.sqrt((centerX - i)**2 + (centerY - j)**2))
            if distance < 0.00001:
                continue
            yAxisScale[distance] += 1
            yAxis[distance] += skPicture[i,j]
    return zip(xAxis, yAxis/yAxisScale)

def plotSKAverage(skavg):
    #for scaling while debugging
    #look up the exact scaling stuff that Pascal's program had
    #it should be on the modified s(k) program that I did
    pixelToMicroM = 2.56
    pixelsInXRange = 200
    py.plot([x/(2*3.14159/(2.56/pixelToMicroM)/pixelsInXRange) for (x,y) in skavg], [y for (x,y) in skavg])
    py.show()


def skPlotCounter(var, val):
    def decorate(func):
        setattr(func, var, val)
        return func
    return decorate

@skPlotCounter("count", 0)
def plot(sofk):
    plot.count += 1
    py.figure(1)
    py.clf()
    py.imshow(numpy.log10(sofk))
    py.savefig(str(plot.count) + 'frame.png')

#the input of this is something that has been transformed using fft
def plotSK(sofk):
    py.figure(1)
    py.clf()
    py.imshow(numpy.log10(sofk))
    py.show()

def run(timeStep):
    plotSK(runSK(timeStep))
    #plot(runSK(timeStep))

#takes in a list of sofks (so it's been through the fft thing already)
def accumulateTimeSteps(sofkList):
    #set the boundary of the image to be the number of pixels in the first time step
    image = numpy.zeros((len(listOfTimesteps[0]), len(listOfTimesteps[0][0])))
    for s in listOfTimesteps:
        try:
            image += s
        except:
            #the sizes do not match
            continue
    return image

