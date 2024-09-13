#$HOME/.cdsapirc
#url: https://cds.climate.copernicus.eu/api/v2
#key: 32793:d80ad37e-b535-4a5d-baec-f1587633171d

#Here the key parameter is the area and the first two values are starting latitude and longitude followed by the ending latitude and longitude. 

#import cdsapi
import time
import os
import glob
import copernicusmarine
from datetime import datetime, timedelta

dataset = 'PHY001024_FORECAST'
datapath = 'PHY_001_024_FORECAST'

today_now = datetime.now()
start_ = today_now - timedelta(days = 10)
end_ = today_now + timedelta(days = 10)

start_here = ('%04d-%02d-%02d' % (start_.year,start_.month,start_.day))
end_there = ('%04d-%02d-%02d' % (end_.year,end_.month,end_.day))

server_path = '/server/DISK1/Dataset_Sync/'
#server_path = '/server/DISK3/Dataset_Sync/'
file=dataset+'_'+('%04d-%02d-%02d'%(today_now.year,today_now.month,today_now.day))+'.nc'
path=server_path+datapath
full_path = path+'/'+file
print(full_path)

#OLD MOTU
#download_args_template_motu = '--motu;http://nrt.cmems-du.eu/motu-web/Motu;--service-id;GLOBAL_ANALYSISFORECAST_PHY_001_024-TDS;--product-id;cmems_mod_glo_phy_anfc_0.083deg_PT1H-m;--longitude-min;14;--longitude-max;34;--latitude-min;-40;--latitude-max;-26;--date-min;$START 12:00:00;--date-max;$END 12:00:00;--depth-min;0.493;--depth-max;5727.918000000001;--variable;thetao;--variable;zos;--variable;uo;--variable;vo;--out-dir;$PATH;--out-name;$FILE;--user;dbailey;--pwd;SEtiyymy'
#download_args_template = 'python -m motuclient '+download_args_template_motu.replace(';',' ')

#NEW COPERNICUS TOOLBOX
download_args = {
"username": "dbailey",
"password": "SEtiyymy",
#"overwrite_metadata_cache": True,
"force_download": True,
"overwrite_output_data": True,
"service": "arco-time-series",
"dataset_id": "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
"variables": ["thetao","zos","uo","vo"],
"minimum_longitude": 14,
"maximum_longitude": 34,
"minimum_latitude": -40,
"maximum_latitude": -26,
"minimum_depth": 0.493,
"maximum_depth": 5727.918000000001,
"start_datetime": "$STARTT12:00:00",
"end_datetime": "$ENDT12:00:00",
"output_directory": "$PATH",
"output_filename": "$FILE"
}

for key, value in download_args.items():
    if type(value) is str:
        value = value.replace("$START",start_here)
        value = value.replace("$END",end_there)
        value = value.replace("$PATH",path)
        value = value.replace("$FILE",file)
        download_args[key] = value

print('Performing Catchup...')
print(download_args)

copernicusmarine.subset(**download_args)

# Remove everything except the latest file
filenames = [entry.name for entry in sorted(os.scandir(path),key=lambda x: x.stat().st_mtime, reverse=True)]
for filename in filenames[1:]:
    if not filename=="analysis":
        filename_path = os.path.join(path,filename)
        print("Removing: "+filename_path)
        os.remove(filename_path)
