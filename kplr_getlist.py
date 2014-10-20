import kplr
import matplotlib.pyplot as plt
import numpy as np
import functions
client = kplr.API()

star = client.star(8800954)

lcs = star.get_light_curves(short_cadence=False)

med_flux_list = []
filter_size = 80

time_list, flux_list, ferr_list = [], [], []
for lc in lcs:
    with lc.open() as f:
        # The lightcurve data are in the first FITS HDU.
        hdu_data = f[1].data
        time, flux, ferr = functions.fix_data(hdu_data)
        time_list.append(time)
        flux_list.append(flux)
        median = functions.median_filter(flux, filter_size)
        ferr_list.append((ferr / median)**2)
        med_flux_list.append(flux / median)

time = np.concatenate(time_list)
flux = np.concatenate(flux_list)
med_flux = np.concatenate(med_flux_list)

depth = 0.003
width = 0.1

#Run the search
ln_like_perfect = np.asarray([functions.pre_ln_like(med_flux, functions.push_box_model(o, depth, width, time)) for o in time])
ln_like_flat = functions.pre_ln_like(med_flux, functions.flat_model(time))

#Subtract off teh ln_like_flat as it is just a constant.
ln_like_array = ln_like_perfect - ln_like_flat
# index_maxi_like = np.argmax(ln_like_array)


fig1 = plt.figure()
sub1 = fig1.add_subplot(211)
sub1.plot(time, flux, ',k')
sub1.set_xlabel("Days")
sub1.set_ylabel("Raw Flux")

sub2 = fig1.add_subplot(212)
sub2.plot(time, med_flux, ',k')
sub2.set_xlabel("Days")
sub2.set_ylabel("Median-filtered Flux")

fig2 = plt.figure()
sub3 = fig2.add_subplot(211)
sub3.plot(time, med_flux, ',k')
sub3.set_xlabel("Days")
sub3.set_ylabel("Median-filtered Flux")

sub4 = fig2.add_subplot(212)
sub4.plot(time, ln_like_array, ',b')
sub4.set_xlabel("Days")
sub4.set_ylabel("Ln_Like")

plt.show()

