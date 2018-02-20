import sys
import numpy as np
import matplotlib.pyplot as plt
import read_lammpstrj as rl
#center = [x,y,z] as float
#frame_xyz = [[x,y,z]] as float (the xyz positions for a single frame)
def compute_distribution(center, frame_xyz, cutoff, resolution):
    bins = cutoff/resolution
    histogram = [0 for a in range(int(np.ceil(bins)))]
    if bins == 0:
        print "You probably should enter cutoff or resolution as a float :("
    for line in frame_xyz:
        dist2 = sum(map(lambda (x,y): (x-y)**2, zip(center, line)))
        dist = np.sqrt(dist2)
        if dist < cutoff:
            histogram[int(np.floor(dist))] += 1
    return histogram 

def plot_histogram(yvals, fn = None):
    xvals = [a for a in range(len(yvals))]
    plt.bar(xvals, yvals)
    plt.xlabel("Distance (Angstroms)")
    plt.ylabel("Counts")
    if fn == None:
        plt.show()
    else:
        plt.savefig(fn, dpi=300)
    
#frames = the output of read_tr - it is fine that it has the last two elements of the array as non position data because the zip function will only include the first three 
#skip is the number of frames to skip between each histogram produced
def make_histograms(frames, skip,num_particles, center, cutoff, resolution, output_path = None):
    start = 0
    while start < len(frames) - num_particles:
        current_frame = frames[start:start+num_particles]
        yvals = compute_distribution(center, current_frame, cutoff, resolution) 
        if output_path == None:
            plot_histogram(yvals)
        else:
            plot_histogram(yvals, output_path + str(start) + ".png")
        start += num_particles * skip


#need to fix! it seems like running multiple times doesn't restart make_histograms at the starting point???????????????????
#as in, I computed histograms for center = 10, then center = 80
#and the center = 80 one returned a different result from just computing center = 80 first

def run(fn, skip, output_dir):
    lines = rl.convertToTrackFile(fn) 
    #find the number of particles in a single frame
    #the frame number is the fourth element of the array
    particles = 0
    for l in lines:
        if int(l[3]) != 0:
            break
        else:
            particles += 1
    center = [90.0,0.0,0.0]
    #center = [15.7516, 0.0, 0.0]
    #center = [84.2484, 0.0, 0.0]
    #center = [0.0, 0.0,0.0]
    cutoff = 50.0
    resolution = 1.0
    #make_histograms(lines, skip, particles, center, cutoff, resolution, output_path = '/Users/alexsmith/Desktop/water/try4_restart/histograms/')

    make_histograms(lines, skip, particles, center, cutoff, resolution, output_path = output_dir)


if __name__ == '__main__':
    traj_file = sys.argv[1] 
    output_dir = None
    #not bothering with error checking
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    run(traj_file, 33, output_dir)

