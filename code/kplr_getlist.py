import kplr
import matplotlib as mpl
mpl.rcParams['axes.formatter.useoffset']=False
mpl.rcParams['figure.figsize'] = 12,9
# import matplotlib.pyplot as plt
plt = mpl.pyplot
import numpy as np
import functions
client = kplr.API()

star = client.star(8800954)

lcs = star.get_light_curves(short_cadence=False)

med_flux_list = []
filter_size = 80

time_list, flux_list, var_list, ferr_list = [], [], [], []
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
variance = np.concatenate(var_list)
ferr = np.concatenate(ferr_list)

#depth = 0.003
width = 0.8

#Run the search
ln_like_perfect = np.asarray([functions.ln_like(med_flux, functions.opt_depth_push_model(med_flux, o, width, time), variance) for o in time])
ln_like_flat = functions.ln_like(med_flux, functions.flat_model(time), variance)
#Subtract off the ln_like_flat as it is just a constant.
ln_like_array = ln_like_perfect - ln_like_flat
# ln_like_array = ln_like_perfect
# index_maxi_like = np.argmax(ln_like_array)

#Find the peaks of the ln_like array
index_max_like = np.argmax(ln_like_array)
time_at_like_max = time[index_max_like]
print time_at_like_max
lt = time < (time_at_like_max+width)
ut = (time_at_like_max-width) < time

window_time = lt*ut
w_time = time[window_time]
window_flux = med_flux[window_time]
window_ln_like = ln_like_array[window_time]
window_error = ferr[window_time]

fig1 = plt.figure()
# sub1 = fig1.add_subplot(211)
# sub1.plot(time, flux, ',k')
# sub1.set_xlabel("Days")
# sub1.set_ylabel("Raw Flux")

# sub2 = fig1.add_subplot(212)
# sub2.plot(time, med_flux, ',k')
# sub2.set_xlabel("Days")
# sub2.set_ylabel("Median-filtered Flux")

sub1 = fig1.add_subplot(211)
sub1.plot(time, med_flux, '.k', markersize = 2)
sub1.set_xlabel("Days")
sub1.set_ylabel("Median-filtered Flux")
sub1.grid()

sub2 = fig1.add_subplot(212)
sub2.plot(time, ln_like_array, '.b', markersize = 2)
sub2.set_xlabel("Days")
sub2.set_ylabel("Ln Likelihood")
sub2.grid()

fig2 = plt.figure()
sub3 = fig2.add_subplot(211)
# sub3.plot(time, med_flux, '.k')
sub3.errorbar(w_time, window_flux, yerr=window_error, fmt = '.')
sub3.set_xlabel("Days")
sub3.set_ylabel("Median-filtered Flux")
sub3.grid()

sub4 = fig2.add_subplot(212)
# sub4.plot(time, ln_like_array, '.b')
sub4.plot(w_time, window_ln_like, '.b')
sub4.set_xlabel("Days")
sub4.set_ylabel("Ln_Like")
sub4.grid()

plt.show()

