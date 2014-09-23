import kplr
client = kplr.API()

kplr_id = raw_input('Input kepler ID: ')
star = client.star(kplr_id)
lcs = star.get_light_curves()

time, flux, ferr, quality = [],[],[],[]

for lc in lcs:
	with lc.open() as f:
		hdu_data = f[1].data
		time.append(hdu_data['time'])
		flux.append(hdu_data['sap_flux'])
		ferr.append(hdu_data['sap_flux_err'])
		quality.append(hdu_data['sap_quality'])
