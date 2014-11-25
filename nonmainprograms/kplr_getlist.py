import kplr
import matplotlib as mpl
mpl.rcParams['axes.formatter.useoffset']=False
mpl.rcParams['figure.figsize'] = 13.5,9
# import matplotlib.pyplot as plt
plt = mpl.pyplot
import numpy as np
import functions
import time as timer
from matplotlib.backends.backend_pdf import PdfPages
client = kplr.API()


def main(kplr_id):
    star = client.star(kplr_id)
    width = 1.0

    lcs = star.get_light_curves(short_cadence=False)

    med_flux_list = []
    filter_size = 80

    time_list, flux_list, var_list, ferr_list = [], [], [], []
    start_time = timer.time()
    for lc in lcs:
        with lc.open() as f:
            # The lightcurve data are in the first FITS HDU.
            hdu_data = f[1].data
            time, flux, ferr = functions.fix_data(hdu_data)
            time_list.append(time)
            flux_list.append(flux)
            median = functions.median_filter(flux, filter_size)
            ferr_list.append(ferr/median)
            var_list.append((ferr / median)**2)
            med_flux_list.append(flux / median)

    time = np.concatenate(time_list)
    flux = np.concatenate(flux_list)
    med_flux = np.concatenate(med_flux_list)
    inv_var = 1/(np.concatenate(var_list))
    ferr = np.concatenate(ferr_list)

    print "Loading data", timer.time() - start_time

    #Run the search
    #time_grid makes the time array coarse. This will allow the number of searches to
    #be much less than doing the calculations at all times.
    time_grid = np.arange(min(time), max(time), width/8)
    print time.shape, time_grid.shape
    start_time = timer.time()
    # main_array = np.asarray([functions.get_depth_and_ln_like(med_flux, o, width, time, inv_var) for o in time_grid])
    main_array = np.array([functions.get_depth_and_ln_like(med_flux, o, width, time, inv_var) for o in time_grid])
    transit_boolean_array = np.array([functions.get_transit_boolean(o, width, time) for o in time_grid])
    print "Search time", timer.time() - start_time
    depth_array = main_array[:,0]
    depth_variance_array = main_array[:,1]
    ln_like_array = main_array[:,2]

    #Use the peak_finder function to obtain the boolean arrays used to
    #get the required "transit window" values.
    start_time = timer.time()
    complete_boolean_list, grid_boolean_list, peaks, peak_index = functions.peak_finder(ln_like_array, time, time_grid, width, 5)
    print "Peak finding time", timer.time() - start_time
    print peaks
    print peak_index

    pp = PdfPages('../plots/{0}_width_{1}.pdf'.format(kplr_id, width))
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
    sub3 = fig2.add_subplot(211)
    sub3.plot(time_grid, depth_array, '.b', markersize = 2)
    sub3.set_xlabel("Days")
    sub3.set_ylabel("Depth")
    sub3.grid()

    sub4 = fig2.add_subplot(212)
    sub4.plot(time, flux, '.b', markersize = 2)
    sub4.set_xlabel("Days")
    sub4.set_ylabel("Raw Flux")
    sub4.grid()
    pp.savefig()
    #Plot the peaks and their likelihoods.
    functions.plot_peaks(complete_boolean_list, grid_boolean_list, time, med_flux, ferr, time_grid, ln_like_array, depth_array, transit_boolean_array, peak_index, pp)

    pp.savefig()
    pp.close()
    plt.close('all')

# list_ids = [3644071,8813698,8891318,11465813,10287723,2162635,9214713,12356617,7672940,3239945,2306756,3962440,880945,3230491,736829,11342550,104640629,11709124,8505215,3756801]
# list_ids = [8813697]
start_time = timer.time()
for i in list_ids:
    print "Kepler ID: ", i
    try:
        main(i)
    except ValueError:
        print "Error for ID: ", i
print timer.time() - start_time


