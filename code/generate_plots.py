import matplotlib
matplotlib.rcParams['axes.formatter.useoffset']=False
matplotlib.rcParams['figure.figsize'] = 13.5,9
import functions
import time as timer
from matplotlib.backends.backend_pdf import PdfPages
import h5py
import numpy as np

plt = matplotlib.pyplot

def main(kplr_id, width):
    # file_name = '../picklefiles/{0}_width_{1}.hdf5'.format(kplr_id, width)
    file_name = '../automatically_created_files/{0}_width_{1}.hdf5'.format(kplr_id, width)

    f = h5py.File(file_name, 'r')

    start_time = timer.time()
    time = f["time"][...]
    med_flux = f["med_flux"][...]
    inv_var = f["inv_var"][...]
    ferr = f["ferr"][...]
    time_grid = f["time_grid"][...]
    # transit_boolean_array = f["transit_boolean_array"][...]
    depth_array = f["depth_array"][...]
    depth_variance_array = f["depth_variance_array"][...]
    ln_like_array = f["ln_like_array"][...]

    transit_boolean_array = np.array([functions.get_transit_boolean(o, width, time) for o in time_grid])
    print "Time to load from pickle", timer.time() - start_time

    #Use the peak_finder function to obtain the boolean arrays used to
    #get the required "transit window" values.
    start_time = timer.time()
    complete_boolean_list, grid_boolean_list, peaks, peak_index = functions.peak_finder(ln_like_array, time, time_grid, width, depth_array, 8)
    # print "Peak finding time", timer.time() - start_time
    print peaks
    print peak_index

    # pp = PdfPages('../plots/{0}_width_{1}_from_pickle.pdf'.format(kplr_id, width))
    pp = PdfPages('../auto_plots/KIC_{0}_transitwidth_{1}.pdf'.format(kplr_id, width))

    fig1 = plt.figure()

    sub1 = fig1.add_subplot(211)
    sub1.plot(time, med_flux, '.k', markersize = 2)
    sub1.set_title("KIC: {0}".format(kplr_id))
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

    #Only call the next two functions to check for occultations between two transit events.
    # mid_point_boolean, midpoint = functions.mid_points(time, width, peaks)
    # functions.plot_midpoint(mid_point_boolean, time, med_flux, ferr, pp, midpoint)

    pp.close()
    plt.close('all')

    print "Time to plot", timer.time() - start_time

# list_ids = [3644071,8813698,8891318,11465813,10287723,2162635,9214713,12356617,7672940,3239945,2306756,3962440,880945,3230491,736829,11342550,104640629,11709124,8505215,3756801]
# list_ids = [3756801]
# list_ids = [7672940]
# list_ids = [11465813]
# list_ids=[892977]
# list_ids = [757076]
# id_list = []
# with open('used_id_list.txt', 'r') as text_file:
#     id_list = text_file.readlines()
#     id_list = [kplr_id.rstrip() for kplr_id in id_list]
# print id_list
# width = 1.0
start_time = timer.time()
# for kplr_id in id_list:
#     print "Kepler ID: ", kplr_id
#     try:
#         main(kplr_id, width)
#     except IOError:
#         print "Error for ID: ", kplr_id


##Single star with known kplr id
main(892667, 0.8)
print timer.time() - start_time


