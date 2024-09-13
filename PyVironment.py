import sys
import argparse
import numpy as np
import xarray as xr
import time
import os
import glob
import math, statistics
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap, maskoceans, interp
import numpy as np

def PlotSurface(lat,lon,data,time,index,output):
    x, y = np.meshgrid(lon,lat)
    x2 = np.linspace(x[0][0],x[0][-1],x.shape[1]*5)
    y2 = np.linspace(y[0][0],y[-1][0],y.shape[0]*5)
    x2, y2 = np.meshgrid(x2, y2)

    if(index != -1):
        input_data = data[index,:,:].squeeze()
        time_index = time[index]
    else:
        input_data = data.squeeze()
        time_index = time
        
    surf = interp(input_data,  x[0], y[:, 0], x2, y2,order=1)
    
    plt.figure(figsize=(13, 13))
    map = Basemap(llcrnrlon=lon[1], llcrnrlat=lat[1], urcrnrlon=lon[-1], urcrnrlat=lat[-1], projection="cyl", resolution="l")
    map.bluemarble()
    
    cpf = map.pcolormesh(x2, y2, surf, latlon=True, cmap=cm.gist_rainbow_r) #nipy_spectral jet gist_rainbow_r
    
    colours = 'w'#['w' if level<0 else 'k' for level in cpf.levels]
    cp = map.contour(x2,y2,surf,10,colors=colours)
    plt.clabel(cp, fontsize=8, colors=colours)
    
    cb = plt.colorbar(cpf, orientation='horizontal', location='top', anchor=(0.5, -1), shrink=0.6)
    cb.ax.tick_params(labelsize=10,colors='w') 
    map.drawcoastlines(color='k')
    
    if(index != -1):
        plt.text(20.5,-28,time_index,fontsize=16,color='w')
    #plt.savefig(output, dpi=100)

def find_closest(arr, val): 
    idx = np.abs(arr - val).argmin()
    return idx

def PlotStation(lat,lon,data,time,index,station_lat,station_lon,output):
    x = find_closest(station_lon,lon)
    y = find_closest(station_lat,lat)
    data_at_index = data[index,y,x].squeeze()
    time_series = data[:,y,x].squeeze()
    #print(x,y)
    print(lon[x],lat[y],data_at_index)
    plt.figure()
    plt.plot(time_series)
    plt.axvline(x=index,linewidth=1, color='r')
    plt.text(index+2,data_at_index,data_at_index,fontsize=8,color='r')
    
path_phys = "/server/NFS1/PHY_001_024_FORECAST/"
path_wav = "/server/NFS1/PHY_001_027_FORECAST/"
out_path = "img/"

dataset_phys = 'PHY001024_FORECAST'
dataset_wav = 'PHY001027_FORECAST'

today_now = datetime.now()
suffix = '_'+('%04d-%02d-%02d'%(today_now.year,today_now.month,today_now.day))+'.nc'
#suffix = '_2024-02-26.nc'
file_phys = path_phys+dataset_phys+suffix
file_wav = path_wav+dataset_wav+suffix

#Algoa Bay
station_lat = -33.9
station_lon = 26

# (time,depth,lat,lon)
#https://basemaptutorial.readthedocs.io/en/latest/utilities.html

with xr.open_dataset(file_phys,decode_coords="all") as data:
    lat = data.latitude.values.squeeze()
    lon = data.longitude.values.squeeze()
    phys_time = data.time.values.squeeze()
    u = data.uo.values.squeeze()
    v = data.vo.values.squeeze()
    t = data.thetao.values.squeeze()
    z = data.zos.values.squeeze()

with xr.open_dataset(file_wav,decode_coords="all") as data:
    #lat = data.latitude.values.squeeze()
    #lon = data.longitude.values.squeeze()
    wav_time = data.time.values.squeeze()
    vhm0_ww = data.VHM0_WW.values.squeeze() #Wind Wave Height
    vhm0_sw1 = data.VHM0_SW1.values.squeeze() #Swell Wave 1 Height
    vhm0_sw2 = data.VHM0_SW2.values.squeeze() #Swell Wave 2 Height


wav_data = vhm0_sw1+vhm0_sw2+vhm0_ww
phys_data = t

wav_time_len = len(wav_time)
wav_index = math.floor(wav_time_len/2)+9

phys_time_len = len(phys_time)
phys_index = math.floor(phys_time_len/2)+9

print(phys_index)

phys_var = np.std(phys_data[phys_index:-1,:,:],axis=0)

#for time_index in time_len:
#    input_data = t[time_index,:,:]

PlotStation(lat,lon,wav_data,wav_time,wav_index,station_lat,station_lon,'')
PlotSurface(lat,lon,wav_data,wav_time,wav_index,'')

PlotStation(lat,lon,phys_data,phys_time,phys_index,station_lat,station_lon,'')
PlotSurface(lat,lon,phys_data,phys_time,phys_index,'')

PlotSurface(lat,lon,phys_var,'',-1,'')

