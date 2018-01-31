"""
pygem_input.py is a list of the model inputs that are required to run PyGEM.

These inputs are separated from the main script, so that they can easily be
configured. Other modules can also import these variables to reduce the number
of parameters required to run a function.
"""
# Note: (DEVELOPMENT) Consider structuring the input via steps and/or as
#       required input or have a separate area for variables, parameters that
#       don't really change.
import os
import numpy as np

# ========== LIST OF MODEL INPUT ==============================================
#------- INPUT FOR CODE ------------------------------------------------------
# Model run option - calibration or simulation
option_modelrun_type = 0
#  Option 0 (default) - calibration run (glacier area remains constant)
#  Option 1 - regular model run
# Warning message option
option_warningmessages = 1
#  Warning messages are a good check to make sure that the script is running properly, and small nuances due to 
#  differences in input data (e.g., units associated with GCM air temperature data are correct)
#  Option 1 (default) - print warning messages within script that are meant to
#                      assist user
#  Option 0 - do not print warning messages within script

#------- MODEL PROPERTIES ----------------------------------------------------
# Density of ice [km m-3]
density_ice = 900
# Density of water [km m-3]
density_water = 1000
# Area of ocean [km2]
area_ocean = 362.5 * 10**6
# Heat capacity of ice [J K-1 kg-1]
ch_ice = 1.89 * 10**6
# Thermal conductivity of ice [W K-1 m-1]
k_ice = 2.33
# Model tolerance (used to remove low values caused by rounding errors)
tolerance = 1e-12

#------- INPUT FOR STEP ONE --------------------------------------------------
# STEP ONE: Model Region/Glaciers
#   The user needs to define the region/glaciers that will be used in the model run. The user has the option of choosing
#   the standard RGI regions or defining their own regions.
#   Note: Make sure that all input variables are defined for the chosen option

# ----- Input required for glacier selection options -----
# Glacier selection option
option_glacier_selection = 1
#  Option 1 (default) - enter numbers associated with RGI V6.0
#  Option 2 - glaciers/regions selected via shapefile
#  Option 3 - glaciers/regions selected via new table (other inventory)
# OPTION 1: RGI glacier inventory information
# Filepath for RGI files
rgi_filepath = os.path.dirname(__file__) + '/../RGI/rgi60/00_rgi60_attribs/'
#  file path where the rgi tables are located on the computer
#  os.path.dirname(__file__) is getting the directory where the pygem model is running.  '..' goes up a folder and then 
#  allows it to enter RGI and find the folders from there.
# Latitude column name
lat_colname = 'CenLat'
# Longitude column name
lon_colname = 'CenLon'
# Elevation column name
elev_colname = 'elev'
# Index name
indexname = 'GlacNo'
# 1st order region numbers (RGI V6.0)
rgi_regionsO1 = [15]
#  enter integer(s) in brackets, e.g., [13, 14]
# 2nd order region numbers (RGI V6.0)
rgi_regionsO2 = 'all'
# rgi_regionsO2 = [1]
#  enter 'all' to include all subregions or enter integer(s) in brackets to specify specific subregions, e.g., [5, 6]. 
# RGI glacier number (RGI V6.0)
rgi_glac_number = ['03473', '03733']
#rgi_glac_number = 'all'
#  enter 'all' to include all glaciers within (sub)region(s) or enter a string of complete glacier number for specific 
#  glaciers, e.g., ['05000', '07743'] for glaciers '05000' and '07743'
# Dictionary of hypsometry filenames
rgi_dict = {
            13: '13_rgi60_CentralAsia.csv',
            14: '14_rgi60_SouthAsiaWest.csv',
            15: '15_rgi60_SouthAsiaEast.csv'}
# Columns in the RGI tables that are not necessary to include in model run.
rgi_cols_drop = ['GLIMSId','BgnDate','EndDate','Status','Connect','Surging','Linkages','Name']
#  this will change as model develops to include ice caps, calving, etc.
# OPTION 2: Select/customize regions based on shapefile(s)
# Enter shapefiles, etc.


#------- INPUT FOR STEP TWO --------------------------------------------------
# STEP TWO: Additional model setup
#   Additional model setup that has been separated from the glacier selection in step one in order to keep the input 
#   organized and easy to read.
#
# ----- Input required for glacier hypsometry -----
# extract glacier hypsometry according to Matthias Huss's ice thickness files (area and width included as well)
#  Potential option - automatically extract 50m hypsometry from RGI60
#  Potential option - extract glacier hypsometry and mass balance from David Shean's measurements using high-res DEMs
# Elevation band height [m]
binsize = 10
# Filepath for the hypsometry files
hyps_filepath = os.path.dirname(__file__) + '/../IceThickness_Huss/bands_10m_DRR/'
# Dictionary of hypsometry filenames
hyps_filedict = {
                13: 'area_13_Huss_CentralAsia_10m.csv',
                14: 'area_14_Huss_SouthAsiaWest_10m.csv',
                15: 'area_15_Huss_SouthAsiaEast_10m.csv'}
# Extra columns in hypsometry data that will be dropped
hyps_colsdrop = ['RGI-ID','Cont_range']
# Filepath for the ice thickness files
thickness_filepath = os.path.dirname(__file__) + '/../IceThickness_Huss/bands_10m_DRR/'
# Dictionary of thickness filenames
thickness_filedict = {
                13: 'thickness_13_Huss_CentralAsia_10m.csv',
                14: 'thickness_14_Huss_SouthAsiaWest_10m.csv',
                15: 'thickness_15_Huss_SouthAsiaEast_10m.csv'}
# Extra columns in ice thickness data that will be dropped
thickness_colsdrop = ['RGI-ID','Cont_range']
# Filepath for the width files
width_filepath = os.path.dirname(__file__) + '/../IceThickness_Huss/bands_10m_DRR/'
# Dictionary of thickness filenames
width_filedict = {
                13: 'width_13_Huss_CentralAsia_10m.csv',
                14: 'width_14_Huss_SouthAsiaWest_10m.csv',
                15: 'width_15_Huss_SouthAsiaEast_10m.csv'}
# Extra columns in ice thickness data that will be dropped
width_colsdrop = ['RGI-ID','Cont_range']

""" NEED TO CODE VOLUME-LENGTH SCALING """
# Option - volume-length scaling
#   V_init = c_v * Area_init ^ VA_constant_exponent
#   where L is the change in
#   Need to define c_l and q, which are volume length scaling constants


# ----- Input required for model time frame -----
# Note: models are required to have complete data for each year such that refreezing, scaling, etc. are consistent for 
#       all time periods.
# Leap year option
option_leapyear = 1
#  Option 1 (default) - leap year days are included, i.e., every 4th year Feb 29th is included in the model, so 
#                       days_in_month = 29 for these years.
#  Option 0 - exclude leap years, i.e., February always has 28 days
# Water year option
option_wateryear = 1
#  Option 1 (default) - use water year instead of calendar year (ex. 2000: Oct 1 1999 - Sept 1 2000)
#  Option 0 - use calendar year
# Water year starting month
wateryear_month_start = 10
# First month of winter
winter_month_start = 10
#  for HMA, winter is considered  October 1 - April 30
# First month of summer
summer_month_start = 5
#  for HMA, summer is considered May 1 - September 30
# Option to use dates based on first of each month or those associated with the climate data
option_dates = 1
#  Option 1 (default) - use dates associated with the dates_table that user generates (first of each month)
#  Option 2 - use dates associated with the climate data (problem here is that this may differ between products)
# Model timestep
timestep = 'monthly'
#  enter 'monthly' or 'daily'
# First year of model run
startyear = 2000
#  water year example: 2000 would start on October 1999, since October 1999 - September 2000 is the water year 2000
#  calendar year example: 2000 would start on January 2000
# Last year of model run
endyear = 2015
#  water year example: 2000 would end on September 2000
#  calendar year example: 2000 would end on December 2000
# Number of years for model spin up [years]
spinupyears = 0

# ----- Input required for initial surface type -----
# Initial surface type options
option_surfacetype_initial = 1
#  Option 1 (default) - use median elevation to classify snow/firn above the median and ice below.
#   > Sakai et al. (2015) found that the decadal ELAs are consistent with the median elevation of nine glaciers in High 
#     Mountain Asia, and Nuimura et al. (2015) also found that the snow line altitude of glaciers in China corresponded
#     well with the median elevation.  Therefore, the use of the median elevation for defining the initial surface type
#     appears to be a fairly reasonable assumption in High Mountain Asia. 
#  Option 2 (Need to code) - use mean elevation instead
#  Option 3 (Need to code) - specify an AAR ratio and apply this to estimate initial conditions
# Firn surface type option
option_surfacetype_firn = 1
#  Option 1 (default) - firn is included
#  Option 0 - firn is not included
# Debris surface type option
option_surfacetype_debris = 0
#  Option 0 (default) - debris cover is not included
#  Option 1 - debris cover is included
#   > Load in Batu's debris maps and specify for each glacier
#   > Determine how DDF_debris will be included


#------- INPUT FOR STEP THREE ------------------------------------------------
# STEP THREE: Climate Data
#   The user has the option to choose the type of climate data being used in the
#   model run, and how that data will be downscaled to the glacier and bins.
# Option to downscale GCM data
option_gcm_downscale = 1
# Option 1 (default): select climate data based on nearest neighbor
# Filepath to GCM variable files
gcm_filepath_var = os.path.dirname(__file__) + '/../Climate_data/ERA_Interim/'
#  _var refers to variable data; NG refers to New Generation of CMIP5 data, i.e., a homogenized dataset
# Filepath to GCM fixed variable files
gcm_filepath_fx = os.path.dirname(__file__) + '/../Climate_data/ERA_Interim/'
#  _fx refers to time invariant (constant) data
# Temperature filename
gcm_temp_filename = 'ERAInterim_AirTemp2m_DailyMeanMonthly_1995_2016.nc'
#  netcdf files downloaded from cmip5-archive at ethz or ERA-Interim reanalysis data (ECMWF)
# Precipitation filename
gcm_prec_filename = 'ERAInterim_TotalPrec_DailyMeanMonthly_1979_2017.nc'
# Elevation filename
gcm_elev_filename = 'ERAInterim_geopotential.nc'
# Temperature variable name given by GCM
gcm_temp_varname = 't2m'
#  't2m' for ERA Interim, 'tas' for CMIP5
# Precipitation variable name given by GCM
gcm_prec_varname = 'tp'
#  'tp' for ERA Interim, 'pr' for CMIP5
# Elevation variable name given by GCM
gcm_elev_varname = 'z'
#  'z' for ERA Interim, 'orog' for CMIP5
# Latitude variable name given by GCM
gcm_lat_varname = 'latitude'
#  'latitude' for ERA Interim, 'lat' for CMIP5
# Longitude variable name given by GCM
gcm_lon_varname = 'longitude'
#  'longitude' for ERA Interim, 'lon' for CMIP5
# Time variable name given by GCM
gcm_time_varname = 'time'


#------- INPUT FOR STEP FOUR -------------------------------------------------
# STEP FOUR: Glacier Evolution
#   Enter brief description of user options here.

# Lapse rate from gcm to glacier [K m-1]
lr_gcm = -0.0065
# Lapse rate on glacier for bins [K m-1]
lr_glac = -0.0065
# Precipitation correction factor [-]
prec_factor = 0.3
#  k_p in Radic et al. (2013)
#  c_prec in Huss and Hock (2015)
# Precipitation gradient on glacier [% m-1]
prec_grad = 0.0001

DDF_ice = 7.2 * 10**-3
# DDF ice (m w.e. d-1 degC-1)
# note: '**' means to the power, so 10**-3 is 0.001
# DDF snow (m w.e. d-1 degC-1)
DDF_snow = 4.0 * 10**-3
# Temperature threshold for snow (C)
T_snow = 0

#   Huss and Hock (2015) T_snow = 1.5 deg C with +/- 1 deg C for ratios
DDF_firn = np.mean([DDF_ice, DDF_snow])
# DDF firn (m w.e. d-1 degC-1)
# DDF_firn is average of DDF_ice and DDF_snow (Huss and Hock, 2015)
DDF_debris = DDF_ice
#  debris DDF is currently equivalent to ice
# Reference elevation options for downscaling climate variables
option_elev_ref_downscale = 'Zmed'
#  Option 1 (default) - 'Zmed', median glacier elevation
#  Option 2 - 'Zmax', maximum glacier elevation
#  Option 3 - 'Zmin', minimum glacier elevation (terminus)
# Temperature adjustment options
option_adjusttemp_surfelev = 1
#  Option 1 (default) - yes, adjust temperature
#  Option 2 - do not adjust temperature
# Surface type options
option_surfacetype = 1
#  How is surface type considered, annually?
# Surface ablation options
option_surfaceablation = 1
#  Option 1 (default) - DDF for snow, ice, and debris
# Surface accumulation options
option_accumulation = 1
#  Option 1 (default) - Single threshold (<= snow, > rain)
#  Option 2 - single threshold +/- 1 deg uses linear interpolation
# Refreezing model options
option_refreezing = 2
#  Option 1 (default) - heat conduction approach (Huss and Hock, 2015)
#  Option 2 - annual air temperature appraoch (Woodward et al., 1997)
# Refreeze depth [m]
refreeze_depth = 10
# Refreeze month
refreeze_month = 10
#  required for air temperature approach to set when the refreeze is included
# Downscale precipitation to bins options
option_prec2bins = 1
#  Option 1 (default) - use of precipitation bias factor to adjust GCM value and precipitation gradient on the glacier
#  Option 2 (need to code) - Huss and Hock (2015), exponential limits, etc.
# Downscale temperature to bins options
option_temp2bins = 1
#  Option 1 (default) - lr_gcm and lr_glac to adjust temperature from gcm to the glacier reference (default: median), 
# Melt model options
option_melt_model = 1
#  Option 1 (default) DDF
# Mass redistribution / Glacier geometry change options
option_massredistribution = 1
#  Option 1 (default) - Mass redistribution based on Huss and Hock (2015), i.e., volume gain/loss redistributed over the 
#                       glacier using empirical normalized ice thickness change curves
# Cross-sectional glacier shape options
option_glaciershape = 1
#  Option 1(default) - parabolic (used by Huss and Hock, 2015)
#  Option 2 - rectangular
#  Option 3 - triangular
# Glacier width option
option_glaciershape_width = 1
#  Option 0 (default) - do not include
#  Option 1 - include
# Advancing glacier ice thickness change threshold
icethickness_advancethreshold = 5
#  Huss and Hock (2015) use a threshold of 5 m
# Percentage of glacier considered to be terminus
terminus_percentage = 20
#  Huss and Hock (2015) use 20% to calculate new area and ice thickness

#------- INPUT FOR STEP FOUR -------------------------------------------------
# STEP FIVE: Output
netcdf_filenameprefix = 'PyGEM_output_rgiregion'
netcdf_filepath = '../Output/'

# Output files [bin, bin_annual, glacier, glacier_annual]
#input.output_temp =                 [1, 0, 0, 0]
#input.output_prec =                 [1, 0, 0, 0]
#input.output_acc =                  [0, 0, 1, 0]
#input.output_refreeze =             []
#input.output_melt =                 []
#input.output_melt_glaccomponent =   []
#input.output_melt_snowcomponent =   []
#input.output_melt_refrcomponent =   []
#input.output_frontalablation =      []
#input.massbal_clim =                []
#input.massbal_total =               []
#input.massbal =                     [0, 0, 1, 0]
#input.output_snowdepth =            []
#input.output_area =                 []
#input.output_icethickness =         []
#input.output_volume =               []
#input.output_width =                []
#input.output_surfacetype =          []
#input.output_runoff =               []
#input.output_ELA =                  []
#input.output_AAR =                  []
#input.output_snowline =             []









