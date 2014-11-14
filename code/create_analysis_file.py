import kplr
import numpy as np
import functions
import time as timer
client = kplr.API()

def main(kplr_id, width):
    star = client.star(kplr_id)

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
    med_flux = np.concatenate(med_flux_list)
    inv_var = 1/(np.concatenate(var_list))
    ferr = np.concatenate(ferr_list)

    file_name = '../picklefiles/{0}_width_{1}.p'.format(kplr_id, width)
    write_file = open(file_name, 'wb')
    
    time.dump(write_file)
    med_flux.dump(write_file)
    inv_var.dump(write_file)
    ferr.dump(write_file)

    print "Loading data", timer.time() - start_time

    #Run the search
    #time_grid makes the time array coarse. This will allow the number of searches to
    #be much less than doing the calculations at all times.
    time_grid = np.arange(min(time), max(time), width/8)

    time_grid.dump(write_file)

    print time.shape, time_grid.shape
    start_time = timer.time()
    # main_array = np.asarray([functions.get_depth_and_ln_like(med_flux, o, width, time, inv_var) for o in time_grid])
    main_array = np.array([functions.get_depth_and_ln_like(med_flux, o, width, time, inv_var) for o in time_grid])
    transit_boolean_array = np.array([functions.get_transit_boolean(o, width, time) for o in time_grid])
    print "Search time", timer.time() - start_time
    depth_array = main_array[:,0]
    depth_variance_array = main_array[:,1]
    ln_like_array = main_array[:,2]

    transit_boolean_array.dump(write_file)
    depth_array.dump(write_file)
    depth_variance_array.dump(write_file)
    ln_like_array.dump(write_file)

    write_file.close()

# list_ids = [3644071,8813698,8891318,11465813,10287723,2162635,9214713,12356617,7672940,3239945,2306756,3962440,880945,3230491,736829,11342550,104640629,11709124,8505215,3756801]
list_ids = [3756801, 7672940]
width = 0.5
start_time = timer.time()
for i in list_ids:
    print "Kepler ID: ", i
    try:
        main(i, width)
    except ValueError:
        print "Error for ID: ", i
print timer.time() - start_time


