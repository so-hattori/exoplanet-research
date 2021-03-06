import kplr
import numpy as np
import functions
import time as timer
import h5py

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
    
    print "Loading data", timer.time() - start_time

    #Run the search
    #time_grid makes the time array coarse. This will allow the number of searches to
    #be much less than doing the calculations at all times.
    time_grid = np.arange(min(time), max(time), width/8)


    print time.shape, time_grid.shape
    start_time = timer.time()
    # main_array = np.asarray([functions.get_depth_and_ln_like(med_flux, o, width, time, inv_var) for o in time_grid])
    main_array = np.array([functions.get_depth_and_ln_like(med_flux, o, width, time, inv_var) for o in time_grid])
    # transit_boolean_array = np.array([functions.get_transit_boolean(o, width, time) for o in time_grid])
    print "Search time", timer.time() - start_time
    depth_array = main_array[:,0]
    depth_variance_array = main_array[:,1]
    ln_like_array = main_array[:,2]

    ###OPEN, WRITE, CLOSE DATA TO FILE###
    # file_name = '../picklefiles/{0}_width_{1}.hdf5'.format(kplr_id, width)
    file_name = '../automatically_created_files/{0}_width_{1}.hdf5'.format(kplr_id, width)

    f = h5py.File(file_name, 'w')
    f.create_dataset("time", data=time)
    f.create_dataset("med_flux", data=med_flux)
    f.create_dataset("inv_var", data=inv_var)
    f.create_dataset("ferr", data=ferr)
    f.create_dataset("time_grid", data=time_grid)
    # f.create_dataset("transit_boolean_array", data=transit_boolean_array)
    f.create_dataset("depth_array", data=depth_array)
    f.create_dataset("depth_variance_array", data=depth_variance_array)
    f.create_dataset("ln_like_array", data=ln_like_array)
    print time.shape
    # print transit_boolean_array.shape
    # assert 0

    f.close()

# list_ids = [3644071,8813698,8891318,11465813,10287723,2162635,9214713,12356617,7672940,3239945,2306756,3962440,880945,3230491,736829,11342550,104640629,11709124,8505215,3756801]
list_ids = [7672940]
# list_ids = [3756801]
# list_ids = [11465813]
# list_ids=[892977]
# list_ids = [757076]

width = 1.0
start_time = timer.time()

client = kplr.API()
# lcs = client.light_curves(sci_data_quarter=5, max_records=20, order='ktc_kepler_id')
# id_list = [l.ktc_kepler_id for l in lcs]

# for kplr_id in id_list:
#     print "Kepler ID: ", kplr_id
#     try:
#         with open('used_id_list.txt', 'a') as text_file:
#             text_file.write("%s\n" % kplr_id)
#         main(kplr_id, width)
#     except ValueError:
#         with open('id_error_log.txt', 'a') as error_file:
#             error_file.write("%s\n" % kplr_id)
#         print "Error for ID: ", kplr_id

###Single star analysis with a known kplr id
main(892667, 0.8)


print timer.time() - start_time


