import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
#from glob import glob
import xarray as xr
import numpy as np
from datetime import datetime
import re
import matplotlib as mpl
import pickle
 
from satpy.scene import Scene
from satpy.utils import debug_on
#debug_on()

class Area:
    def __init__(self, north=None, south=None, west=None, east=None, ):
        self.north = north
        self.south = south
        self.west = west
        self.east = east


def grid_totals(llats, llons, area=None, reso=1):
    """
    Computes the totals of lightning LGR/LFL lat/lon points per grid cell.
    Args:
      llats, llons = xarray data arrays of latitudes and longitudes.
      area = an area class object representing the area of interest.
      reso = grid resolution in degrees.
    Returns:
      totals = xarray data array containing the latitudes, longitudes and
        totals of lightning observations for each grid cell.
    """

    # The lat/lon bounds of the grid.
    if area is not None:
        latn, lats, lonw, lone = area.north, area.south, area.west, area.east
    else:
        latn, lats, lonw, lone = 85, -85, -85, 85

    # All lat and lon bins as 1d arrays.
    lat_bins = np.arange(lats, latn + reso, reso)
    lon_bins = np.arange(lonw, lone + reso, reso)

    totals = np.histogram2d(llons, llats, bins=(lon_bins, lat_bins),
                            range=[(lonw, lone), (lats, latn)])[0]

    totals = xr.DataArray(totals.T, coords=[lat_bins[:-1], lon_bins[:-1]],
        dims=['latitude', 'longitude'])

    totals['latitude'] = totals['latitude'] + reso / 2
    totals['longitude'] = totals['longitude'] + reso / 2

    return totals


def plot_li_fov_polygons(ax, projection=ccrs.PlateCarree()):
    """
    Plot the polygons of LI camera field-of-views on a map.
    Args:
      ax: axis with cartopy map to plot the polygons on.
    Returns:
      None, plots the polygons on the map.
    """

    polygons = [{'name': 'west', 'color': 'dodgerblue', 'file_path': './li_fov/LI_west.p'},
                {'name': 'north', 'color': 'darkorange', 'file_path': './li_fov/LI_north.p'},
                {'name': 'east', 'color': 'green', 'file_path': './li_fov/LI_east.p'},
                {'name': 'south', 'color': 'darkred', 'file_path': './li_fov/LI_south.p'}]

    for polygon in polygons:
        file_path = polygon['file_path']
        with open(file_path, 'rb') as pickle_file:
            poly = pickle.load(pickle_file)
        color = polygon['color']
        ax.add_geometries(poly, crs=projection, facecolor='none', edgecolor=color, lw=2)

    return


def plot_accmap(acc_grid, projection=ccrs.PlateCarree(), gridlines=True,
    vmax=None, area=None, plot_fov=False, title='', fname=None):
    """
    Plot the accumulated lightning locations heatmap.
    Args:
      acc_grid = xarray ready-to-plot lightning accumulation array.
      projection = map projection.
      gridlines = if True then plot map gridlines.
      vmax  = maximum value of observations per grid cell for colour scale.
      area = list defing the bounding box of the area or interest like [north, south, west, east].
      plot_fov = if True then plot the 4 LI camera field-of-views on the map.
      title = plot title str.
      fname = output file name, if given then save plot as file.
    Returns:
      None, displays and/or saves the plot.
    """

    if area is None:
        area = Area(85, -85, -85, 85)
    else:
        area = Area(area[0], area[1], area[2], area[3])

    # Create the figure, plot background map and title.
    fig, ax = plt.subplots(subplot_kw=({'projection': projection}))
    format_fig_size(fig, area)
    ax = plotmap(ax, gridlines=gridlines, area=area)
    fig.suptitle(title, y=0.92)

    # Plot the heatmap.
    if not vmax:
        vmax=10**5
    acc_grid.plot(ax=ax, transform=ccrs.PlateCarree(),
        norm=mpl.colors.LogNorm(vmin=1, vmax=vmax), cmap='gist_rainbow_r')

    # Plot area ploygons if required.
    if plot_fov:
        plot_li_fov_polygons(ax, projection=projection)

    # Save if file name is given.
    if fname:
        fig.savefig(fname, dpi=300, bbox_inches='tight')
        print(f'Saved the plot as {fname}!')

    return


def plotmap(ax, set_global=False, gridlines=False, area=None):
    """
    Initializes the figure and plots cartopy map with coastlines, country
    borders and gridlines.
    Args:
      ax = matplotlib axis object to plot the map on.
      set_global = if True then set the extent of the ax to the limits of the
        projection (can be actually smaller than global if national projection).
      gridlines = if True then plot gridlines.
      area = an area class object representing the area of interest.
    Returns:
      ax = input matplotlib axis object with the map.
    """
 
    # Add main map features.
    ax.add_feature(cartopy.feature.LAND)
    ax.add_feature(cartopy.feature.COASTLINE, zorder=2)
    ax.add_feature(cartopy.feature.BORDERS)
    ax.set_xlabel('lon')
    ax.set_ylabel('lat')
 
    # Set to the extent of the projection if required.
    if set_global:
        ax.set_global()
 
    # Plot gridlines if required.
    if gridlines:
        try:
            gridlines = ax.gridlines(draw_labels=True)
            gridlines.top_labels = None
            gridlines.right_labels = None
        except TypeError:
            gridlines = ax.gridlines()
 
    # Zoom into a sepecific area.
    if area:
        ax.set_xlim(area.west, area.east)
        ax.set_ylim(area.south, area.north)
 
    return ax
 
 
def format_fig_size(fig, area):
    """
    Spatial regions can be horizontal or vertical in shape. This function
    measures the sides of the lat/lon box in degrees and formats the figure
    size for best layout in the saved image (not so optimal for the live image
    window.
    Args:
      fig = matplotlib fig object to format.
      area = an area class object representing the area of interest.
    Returns:
      None, sets the figure width and height to the computed value, based
      on the shape of the area.
    """
 
    y_x_ratio = (area.north - area.south) / (area.east - area.west)
    # 8 and 6 are experimental and work best on saved plots.
    width = int(8 / y_x_ratio)
    height = 6
    fig.set_figwidth(width)
    fig.set_figheight(height)
 
 
def plot_lmap(lats, lons, time, projection=ccrs.PlateCarree(), gridlines=True,
              area=None, area_nswe=None, plot_fov=False, title=None):
    """
    Plot events/groups/flashes, coloured by hour of occurrence.
    Args:
      lats = xarray of latitudes
      lons = array of longitudes
      time = array of time information
      projection = map projection.
      gridlines = if True then plot map gridlines.
      area = an area class object defining the map extent in space.
      area_nswe = 4-element list of North South West East limits for area plot
      plot_fov = if True then plot the 4 LI camera field-of-views on the map.
      title = plot title str.
    Returns:
      None, displays and/or saves the plot.
    """

    if area_nswe is not None:
       area = Area(north=area_nswe[0], south=area_nswe[1], west=area_nswe[2], east=area_nswe[3])
 
    # Create the figure, plot background map and title.
    fig, ax = plt.subplots(subplot_kw=({'projection': projection}))
    format_fig_size(fig, area)
    ax = plotmap(ax, gridlines=gridlines, area=area)
    if title is not None:
        ax.set_title(title)
 
    # Create the colour bar.
    #sm = plt.cm.ScalarMappable(cmap=plt.get_cmap('gist_rainbow_r', 24))
    sm = plt.cm.ScalarMappable(cmap=plt.get_cmap('rainbow', 24))
    sm.set_clim(0, 24)
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_ticks([h + 0.5 for h in range(24)])
    cbar.set_ticklabels([str(h).zfill(2) if h % 2 == 0 else "" for h in range(24)])
    cbar.set_label('Hour of Day')

    # Plot lightning observations.
    #ax.scatter(lons, lats, transform=ccrs.PlateCarree(), cmap='gist_rainbow_r',
    ax.scatter(lons, lats, transform=ccrs.PlateCarree(), cmap='rainbow',               
               marker='x', s=6, c=time.dt.hour, vmin=0, vmax=23)

        # Plot area ploygons if required.
    if plot_fov:
        plot_li_fov_polygons(ax, projection=projection)
 
    return fig,ax
 
 
def plot_lmap_from_filenames(filenames, time_dataset_name, area_nswe=None, title=None, plot_fov=False):
    """
    Plot events/groups/flashes, coloured by hour of occurrence.
    Args:
      filenames = list of files to process
      time_dataset_name = string of time dataset in files
      area_nswe = 4-element list of North South West East limits for area plot
      title = string of plot title
      plot_fov = if True then plot the 4 LI camera field-of-views on the map.
    Returns:
      None, displays and/or saves the plot.
    """
   
    if area_nswe:
       area = Area(north=area_nswe[0], south=area_nswe[1], west=area_nswe[2], east=area_nswe[3])
    else:
       area = Area(85, -85, -85, 85)
        
    if not filenames:
       raise ValueError("No files found. Please check your file path.")
    else:    
        for n, filename in enumerate(filenames):
            scn = Scene([filename], reader="li_l2_nc")
            scn.load([time_dataset_name])
            (lons, lats) = scn[time_dataset_name].attrs['area'].get_lonlats()
            if n == 0:
                times_acc = scn[time_dataset_name].compute()
                lons_acc = xr.DataArray(lons).compute() 
                lats_acc = xr.DataArray(lats).compute() 
            else:
                times_acc = xr.concat([times_acc, scn[time_dataset_name].compute()], dim='y')
                lons_acc = np.concatenate([lons_acc, xr.DataArray(lons).compute() ]) 
                lats_acc = np.concatenate([lats_acc, xr.DataArray(lats).compute() ])

        fig,ax=plot_lmap(lats_acc, lons_acc, times_acc, area=area, title=title, plot_fov=plot_fov)

    return fig,ax

# Function to filter filenames within the given time range
def filter_filenames(filenames, start_dt, end_dt):
    filtered_files = []
    for fname in filenames:
        # Extract the start and end date fields using regex after '_OPE_'
        match = re.search(r'_OPE_(\d{14})_(\d{14})', fname)
        if match:
            # Extract the two date-time strings
            start_str, end_str = match.groups()

            # Convert them to datetime objects
            start_time = datetime.strptime(start_str[:12], "%Y%m%d%H%M")
            end_time = datetime.strptime(end_str[:12], "%Y%m%d%H%M")
            
            # Check if the file is within the desired time range
            
            
            if (start_dt <= start_time <= end_dt) and (start_dt <= end_time <= end_dt):
              
                #print('Filename:',start_time, ' - ', end_time)
                filtered_files.append(fname)
                
    
    return filtered_files




if __name__ == '__main__':

    plot_lmap_from_filenames(filenames, area_nswe, time_dataset_name, title, output_filename)
