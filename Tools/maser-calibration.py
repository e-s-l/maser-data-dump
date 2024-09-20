
# hash-bang for running on ny-mitra in virtual python env (agh)

############################
# BY WAY OF EXPLANATION... #
############################
#
# Tac32 *a*.csv files have time in col 1, & maser2gps in col 4.
# This script takes in this data, &...
# - calculates a parabolic fit 
# - determines the best new drift & new offset parameters based of this fit
# - returns these values, while printing the NR commands required (coz why not)
#

import sys                                      # for argument inputs & program exits

import numpy as np                              # for data handling

from astropy.time import Time                   # for mjd to utc
from datetime import datetime


from scipy.optimize import curve_fit            # for paraoblic fitting

import matplotlib.pyplot as plt                 # for plotting

from scipy.stats import linregress              # for line of best fit

import math


def load_data(data_file):
    """
    Load the data using numpy.
    Assuming known format of data file.
    Interested in first 2 columns.
    """

    try:
        # Load data, assuming the format (time, TIC, ...) 
        data = np.loadtxt(data_file, delimiter=',')
        # get values:
        time = data[:, 0]                       # MJD time format
        tic_mus = data[:, 4]     # col 1 for T, col 4 for A
        return {'time': time, 'tic': tic_mus}
    except OSError:
        print(f"Error: '{data_file}' not found.")
        sys.exit(1)
    except ValueError:
        print("Error: bad values.")
        sys.exit(1)


#########################
# some 2 line utilities #
#########################


def parabola(x, a, b, c):
    return a*x**2 + b*x + c


def first_derivative(x, a, b):
    return 2*a*x + b


def mjd_to_excel(mjd):
    """
    current mjd (days since 17-11-1858) minus the mjd corresponding to the base of excel time (1-1-1900) (ie days between 17-11-1858 and 1-1-1900)
    """
    return mjd - 15019


########
# main #
########

if __name__ == '__main__':

    try:
        ###############
        # import data #
        ###############

        data_file = "test-data/tic.log"
        data_dict = load_data(data_file)    # load the dat dictionary from the file
        mjd = data_dict['time']

        time = mjd_to_excel(mjd)
        #time = mjd

        # print(f"mjd: {mjd}")
        # print(f"time: {time}")

        tic = data_dict['tic']  

        ########################
        # calculate linear fit #
        ########################

        slope, intercept, _, _, _ = linregress(time, tic)
        line = slope * time + intercept

        drift_old = slope
        offset_old = intercept

        print("############################################")
        print(f"NO NO NO.Old DRIFT {drift_old} & OFFSET {offset_old} (Slope & intercept of LOBF)")
        print("############################################")

        ####################################################################
        # I THINK YOUR ASSUMPTIONS HERE ARE WRONG
        # THE VALUES CALCULATED ARE NOT EVEN CLOSE TO THE REGISTER VALUES
        # THE OLDS VALUES CAN MAYBE BE INPUTS
        # OR THIS PROGRAM CAN JUST FIND THE CHANGE COEFFICENT
        ####################################################################

        ###########################
        # calculate parabolic fit #
        ###########################

        params, covariance = curve_fit(parabola, time, tic, maxfev=50000)
        a, b, c = params
        print(f"Fitted parameters: a = {a}, b = {b}, c = {c}")

        fitted_tic = parabola(time, a, b, c)
        fitted_tic_prime = first_derivative(time, a, b) 

        # test plot

        plt.scatter(time, tic, label="Data", color='red')
        plt.plot(time, fitted_tic, label="Fitted Parabola", color='blue')
        plt.plot(time, line, label="LOBF", color='orange',ls ="-.")
        plt.xlabel("time")
        plt.ylabel("TIC")
        plt.legend()
        plt.show()

        #####################################
        # calculate drift and offset values #
        #####################################

        today = time[-1]
        print(f"Today is {today}")

        seconds_per_day = 86400
        factor = seconds_per_day*2.23*(10**-16)   # what actually is this?

        change = ((first_derivative(today, a, b)*(10**-6))/factor)


        print(f"The value to subtract from the current offset is {change}")

        offset_new = offset_old - change

        #######################

        drift_new = 1/((1/drift_old)-((2*a*10**-6)/(seconds_per_day*factor)))

        print("############################################")
        print(f"New DRIFT {drift_new} & OFFSET {offset_new}")
        print("############################################")



    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print("Error: \n", e)
        sys.exit(1)