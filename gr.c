#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <math.h>
#include <string.h>

//Created by Alex Smith July 2016
//Takes in three inputs:
// (1) The file to process (as a track file, although this program can easily be
//modified for a .xyz file by changing a couple of things)
// (2) The file name to ouput the g(r) plot data to
// (3) The particle size (distance units)
// The output is such that you can just do plot 'outputfilename' with lines
// in gnuplot to plot it
// It is TSV with column 1 the x's and column 2 the y's
//to compile: gcc -O3 gr.c -o gr -Wall -Wextra (-O3 definitely reccomended
//for max optimizations)
//if you are not using a mac:
//you will need to add a -lm after the -Wextra
//-o gr speicifes the name of the binary that you want it to make
//run using ./gr (input file) (output file name) (particle size)
//NOTE IT WILL OVERWRITE THE CONTENTS OF THE FILE WITH NAME "ouput file name"

typedef struct point{
    double x;
    double y;
} point;

typedef struct xyz{
    point **points;
    int length;
    int size;
    //size is the number of elements it contains
    //length is the amount allocated (number of elements that can be put here)
} xyz;

void destroyXYZ(xyz ps);
point lineToPoint(char *line);
int fileToPoints(FILE *f, xyz *ps);
int nearestXBin(double xVal, double binSize, int maxDistance, double diameter);
void processTimestep(xyz *ps, xyz *hist, int maxDistance, double binSize, double diameter);
point lineToPointWithTimeStep(char *line, int *timeStep);
int getTimeStep(FILE *f, xyz *ps, int currentStep);

//This takes care of the deallocation for any xyz structures created
void destroyXYZ(xyz ps){
    int i;
    for (i  = 0; i < ps.size; i++){
        free(ps.points[i]);
    }
    free(ps.points);
}

//This function is used if you are using a .xyz file as input -> will need to uncomment 
//one spot in the main function where file to points is called if you modify the program to use this
//returns 1 if there could be more and 0 if it reaches EOF
//It is assumed that once it reaches a valid entry, all of the following entries will be in the same time step until we get to an invalid entry
int fileToPoints(FILE *f, xyz *ps){
    char line[256];
    //the index to put into the array of points
    int i = 0;
    while (fgets(line, 256, f) != NULL){
        point ret;
        ret = lineToPoint(line);
        if (ret.x == -1 && ret.y == -1){
            return 1;
        }
        point *p;
        p = (point *) malloc(sizeof(point));
        *p = ret;
        if (i >= ps->length - 1){
            ps->points = realloc(ps->points, sizeof(point *) * (ps->length + 10000));
            ps->length += 10000;
        }
        ps->points[i] = p;
        ps->size++;
        i++;
    }
    return 0;
}

//this was for an xyz file
point lineToPoint(char *line){
    int u1, u2;
    double x;
    double y;
    int ret;
    ret = sscanf(line, "%d %lf %lf %d", &u1, &x, &y, &u2);
    point p;
    if (ret == 4){
        p.x = x;
        p.y = y;
    }
    else{
        //it couldn't find anything so it must be a new timestep marker
        p.x = -1;
        p.y = -1;
    }
    return p;
}

//This is used to get the next time step in the file (a track file)
//currentStep is the step that is being processed with this function, so that it knows
//when a new step has been reached
int getTimeStep(FILE *f, xyz *ps, int currentStep){
    char line[256];
    //index to put into the array of points
    int i = 0;
    while (fgets(line, 256, f) != NULL){
        point ret;
        int lineTimeStep;
        ret = lineToPointWithTimeStep(line, &lineTimeStep);
        if (lineTimeStep != currentStep){
            //want to go back a line in the file
            fseek(f, -1*strlen(line), SEEK_CUR);
            return 1;
        }
        else{
            point *p;
            p = (point *) malloc(sizeof(point));
            *p = ret;
            //The if covers the case of needing to allocate more for the array
            if (i >= ps->length - 1){
                ps->points = realloc(ps->points, sizeof(point *) * (ps->length + 10000));
                ps->length += 10000;
            }
            ps->points[i] = p;
            ps->size++;
            i++;
        }
    }
    return 0;
}

//this is for a track file
//Takes in a line, parses that line to a point
//the second argument will contain the time step of the line processed
//NOTE HOW IT CHANGES STATE OUTSIDE OF IT'S RETURN 
point lineToPointWithTimeStep(char *line, int *timeStep){
    double x, y, z;
    unsigned long frame, pN;
    int ret;
    ret = sscanf(line, "%lf %lf %lf %lu %lu", &x, &y, &z, &frame, &pN);
    *timeStep = frame;
    point p;
    p.x = x;
    p.y = y;
    return p;

}

//Finds which bin of the histogram to put the point in
int nearestXBin(double xVal, double binSize, int maxDistance, double diameter){
    //can't round up if it's in the highest bin
    int truncated = (int) (xVal/(binSize*diameter));
      
    if (truncated >= maxDistance / binSize - 1){
        return truncated;
    }
    else{
        return round(truncated);
    }
    
}

//Takes a xyz structure of a time step and will update the histogram based upon that time step
void processTimestep(xyz *ps, xyz *hist, int maxDistance, double binSize, double diameter){
    //the g(r) calculation step
    //taken from BianXiao Cui's program in idl
    int i, j;
    maxDistance = maxDistance *diameter;
    int maxDistanceSquared = maxDistance * maxDistance;
    for (i = 0; i < ps->size - 2; i++){
        //put the i'th elements x and y values here for cache stuff
        double xVal = (ps->points[i])->x;
        double yVal = (ps->points[i])->y;
        for (j = i + 1; j < ps->size - 1; j++){
            double xDisplacement = xVal - (ps->points[j])->x;
            double yDisplacement = yVal - (ps->points[j])->y;
            double dSquared = xDisplacement * xDisplacement + yDisplacement * yDisplacement;
            if (dSquared < maxDistanceSquared){
                double distance = sqrt(dSquared);
                int distanceBin = nearestXBin(distance, binSize, maxDistance, diameter);
                (hist->points[distanceBin])->y++;
            }
        }
    }

}


/*
Program flow:
Initialize the structure of points in timestep and of the histogram
Keep looping over the file, and for each time step found in the file:
    Add the points from this time step to the structure with all the points in that time step
    After all of the points have been added, process the histogram
        Process the histogram by:
            Looping over all the pairs of the histogram, and if the distance between two of the
            points is less than maxdis then add it to the appropriate histogram bucket
After all of the time steps have been looped over and we reach the end of the file:
Normalzize the histogram (want it to go to one as the radius goes off to infinity)
*/

int main(int argc, char const *argv[]){
    //program name takes up first arg
    //move this stuff from the main function to it's own function so that longGR
    //can call it
    if (argc < 4){
        printf("%s\n", "This takes in four arguments");
        printf("Args: Input file, output file, diameter\n");
        exit(1);
    }

    FILE *f = fopen(argv[1], "r");
    FILE *output = fopen(argv[2], "w");

    double diameter;

    sscanf(argv[3], "%lf", &diameter);

    xyz ps;
    ps.length = 10000;
    ps.size = 0;
    ps.points = (point **) malloc(sizeof(point *) * 10000);
    //fileToPoints(f, &ps); need this if using the xyz because of quirks with the for loop
    //need to have one file to points before entering the loop

    int maxDistance = 8;
    double binSize = 0.01;
    xyz hist;
    //these should be ints
    hist.size = maxDistance/binSize;
    hist.length = maxDistance/binSize;
    hist.points = (point **) malloc(sizeof(point*) * hist.size);
    //initialize the histogram to be all zeroes
    int i;
    for (i = 0; i < hist.size; i++){
        point *p = (point *) malloc(sizeof(point));
        p->x = i * binSize; 
        p->y = 0;
        hist.points[i] = p;
    }

    //this while loop seems like the thing to parallelize
    //how to do so?

    //keep looping until end of file
    int more;
    int timeSteps = 0;
    while ((more = getTimeStep(f, &ps, timeSteps))){
        processTimestep(&ps, &hist, maxDistance, binSize, diameter);
        //want to zero out ps at the end of the loop
        for (i = 0; i < ps.size; i++){
            ps.points[i]->x = 0;
            ps.points[i]->y = 0;
            free(ps.points[i]);
        }   
        if (timeSteps % 100 == 0){
            printf("Processed the %d time step\n", timeSteps);
        }
        timeSteps++;
        ps.size = 0;
    }
    //need to normalize it now
    for (i = 1; i < hist.size; i++){
        if ((hist.points[i])->y != 0){
            //I belive the 2 might come from the fact that I'm only adding 1 in the histogram update
            double normalizationFactor = 3 * 2 * 3.14159 * i * binSize;
            (hist.points[i])->y = (hist.points[i])->y/normalizationFactor;
        }
    }

    double area = 0;
    for (i = 0; i < hist.size - 1; i++){
        area += 0.5 * ((hist.points[i])->y + (hist.points[i+1])->y);
    }

    for (i = 0; i < hist.size - 1; i++){
       (hist.points[i])->y = (8/binSize) * (hist.points[i])->y / area;
       fprintf(output, "%lf \t %lf\n", (hist.points[i])->x, (hist.points[i])->y);
    }

    destroyXYZ(ps);
    destroyXYZ(hist);
    fclose(f);
    fclose(output);
    return 0;
}
