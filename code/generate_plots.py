import matplotlib
matplotlib.rcParams['axes.formatter.useoffset']=False
matplotlib.rcParams['figure.figsize'] = 13.5,9
import functions
import time as timer
from matplotlib.backends.backend_pdf import PdfPages
import cPickle as pickle

plt = matplotlib.pyplot

def main(kplr_id, width):
    file_name = '../picklefiles/{0}_width_{1}.p'.format(kplr_id, width)
    opened_file = open(file_name, 'rb')

    start_time = timer.time()

    time = pickle.load(opened_file)
    med_flux = pickle.load(opened_file)
    inv_var = pickle.load(opened_file)
    ferr = pickle.load(opened_file)
    time_grid = pickle.load(opened_file)
    transit_boolean_array = pickle.load(opened_file)
    depth_array = pickle.load(opened_file)
    depth_variance_array = pickle.load(opened_file)
    ln_like_array = pickle.load(opened_file)

    opened_file.close()

    print "Time to load from pickle", timer.time() - start_time

    #Use the peak_finder function to obtain the boolean arrays used to
    #get the required "transit window" values.
    start_time = timer.time()
    complete_boolean_list, grid_boolean_list, peaks, peak_index = functions.peak_finder(ln_like_array, time, time_grid, width, 5)
    # print "Peak finding time", timer.time() - start_time
    print peaks
    print peak_index

    pp = PdfPages('../plots/{0}_width_{1}_from_pickle.pdf'.format(kplr_id, width))
    fig1 = plt.figure()

    sub1 = fig1.add_subplot(211)
    sub1.plot(time, med_flux, '.k', markersize = 2)
    sub1.set_xlabel("Days")
    sub1.set_ylabel("Median-filtered Flux")
    sub1.grid()

    sub2 = fig1.add_subplot(212)
    sub2.plot(time_grid, ln_like_array, '.b', markersize = 2)
    sub2.set_xlabel("Days")
    sub2.set_ylabel("ln_Likelihood")
    sub2.grid()

    pp.savefig()

    fig2 = plt.figure()
    sub3 = fig2.add_subplot(111)
    sub3.plot(time_grid, depth_array, '.b', markersize = 2)
    sub3.set_xlabel("Days")
    sub3.set_ylabel("Depth")
    sub3.grid()

    pp.savefig()
    #Plot the peaks and their likelihoods.
    functions.plot_peaks(complete_boolean_list, grid_boolean_list, time, med_flux, ferr, time_grid, ln_like_array, depth_array, transit_boolean_array, peak_index, pp)

    pp.savefig()

    mid_point_boolean = functions.mid_points(time, width)
    functions.plot_midpoint(mid_point_boolean, time, med_flux, ferr, pp)

    pp.close()
    plt.close('all')

    print "Time to plot", timer.time() - start_time

# list_ids = [3644071,8813698,8891318,11465813,10287723,2162635,9214713,12356617,7672940,3239945,2306756,3962440,880945,3230491,736829,11342550,104640629,11709124,8505215,3756801]
# list_ids = [3756801]
list_ids = [3756801, 7672940]
width = 0.5
start_time = timer.time()
for i in list_ids:
    print "Kepler ID: ", i
    try:
        main(i, width)
    except IOError:
        print "Error for ID: ", i
print timer.time() - start_time


