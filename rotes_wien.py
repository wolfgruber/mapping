import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import shape, Polygon
import cartopy.crs as ccrs
import cartopy.feature as cfeature


# reading the input data
bez = gpd.read_file('BEZIRKSGRENZEOGD.json')
zbez = gpd.read_file('ZAEHLBEZIRKOGD.json')
gembau = gpd.read_file('GEMBAUTENFLOGD.json').astype({'WOHNUNGSANZAHL' : float})

#sorting by area
gembau['FLAECHE'] = gembau['geometry'].to_crs(epsg=3416).area
gr_gembau = gembau.sort_values(by='FLAECHE', axis=0, ascending=False, ignore_index=True)

#counting units per census district
count = np.zeros(len(zbez))

for i in range(len(zbez)):
    if i % 10 == 0: print(str(round(i/len(zbez)*100, 2)), end="\r") # progress bar
    for j in range(len(gembau)):
        if zbez.iloc[i]['geometry'].contains(gembau.iloc[j]['geometry']):
            count[i] = gembau.iloc[j]['WOHNUNGSANZAHL'] + count[i]
            
        elif zbez.iloc[i]['geometry'].crosses(gembau.iloc[j]['geometry']):
            ov_area = zbez['geometry'].iloc[i].intersection(gembau.iloc[j]['geometry']).to_crs(epsg=3416).area
            count[i] = (count[i] + gembau.iloc[j]['WOHNUNGSANZAHL'] * gembau.iloc[j]['FLAECHE'] / ov_area)
            
zbez['Wohnungen'] = np.copy(count)


# cleaning the data (norming and dealing with extreme values)
count = count/max(count)

for i in range(len(count)):
    if count[i] > 0.1:
        count[i] = 0.1
count = count/max(count)

_ = plt.hist(count, bins=100)
plt.show()

#creating the plot with matplotlib
cmap = plt.get_cmap('Reds')
col = cmap(count)
col = list(col)

BEZ = cfeature.ShapelyFeature(bez['geometry'], ccrs.PlateCarree())
ZBEZ = cfeature.ShapelyFeature(zbez['geometry'], ccrs.PlateCarree())
GR_BAU = cfeature.ShapelyFeature(gr_gembau.iloc[:100]['geometry'], ccrs.PlateCarree())

plt.figure(dpi=250)
ax = plt.axes(projection=ccrs.Orthographic(central_longitude=16.4, central_latitude=48.2, globe=None))

ax.add_feature(ZBEZ, edgecolor=col, facecolor=col)
ax.add_feature(BEZ, edgecolor='black', facecolor='none')
ax.add_feature(GR_BAU, edgecolor='red', facecolor='red', linewidth=0.4)



ax.set_extent([16.16, 16.6, 48.08, 48.35])

plt.savefig('red_vienna.png')
plt.show()
