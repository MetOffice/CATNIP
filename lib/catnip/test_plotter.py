# Test plotter code
# may not go into final commit but useful here for now
import matplotlib.pyplot as plt
import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs
import um_domain

pole_lat = 70.0
pole_lon = 310.0

# 12lm domain-24
domain_12k = um_domain.UmDomain(delta_lat=0.11, delta_lon=0.11,
                       frstlata=-24.0,
                       frstlona=310.0,
                       polelata=pole_lat, polelona=pole_lon,
                       global_row_length=700, global_rows=550)

domain_4k_v2 = um_domain.UmDomain(delta_lat=0.0405, delta_lon=0.0405,
                      frstlata=-2., frstlona=340.0,
                      polelata=pole_lat, polelona=pole_lon,
                      global_row_length=500, global_rows=432)

# plot all of these on one map

mapextent = [50, 178, -10, 45] # x1, x2, y1, y2

title = ' New 4 & 12 km domains. '
fig = um_domain.domain_plotter(title, mapextent, [domain_4k_v2, domain_12k],
               background='topo', resolution='0.25',
               central_longitude=180)

# list of places to add to the plot
site_list = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Xian',
             'Chongqing', 'Chengdu', 'Harbin', 'Wuhan']

um_domain.plot_cities(site_list)
plt.show()
plt.close()

# and again for 4 km and inner sites
site_list = ['Shanghai', 'Guangzhou', 'Shenzhen', 'Wuhan']

mapextent = [104, 132, 12, 36] # x1, x2, y1, y2
title = 'New 4 km domain'
fig = um_domain.domain_plotter(title, mapextent, [domain_4k_v2],
               background='topo', resolution='0.25',
               central_longitude=180)
um_domain.plot_cities(site_list)

plt.show()
plt.close()
