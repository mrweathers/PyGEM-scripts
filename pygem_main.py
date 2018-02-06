#%% ###################################################################################################################
"""
Python Glacier Evolution Model "PyGEM" V1.0
Prepared by David Rounce with support from Regine Hock.
This work was funded under the NASA-ROSES program (grant no. NNX17AB27G).

PyGEM is an open source glacier evolution model written in python.  The model expands upon previous models from 
Radic et al. (2013), Bliss et al. (2014), and Huss and Hock (2015).
"""
#######################################################################################################################
# This is the main script that provides the architecture and framework for all of the model runs. All input data is 
# included in a separate module called pygem_input.py. It is recommended to not make any changes to this file unless
# you are a PyGEM developer and making changes to the model architecture.
#
#%%========= IMPORT PACKAGES ==========================================================================================
# Various packages are used to provide the proper architecture and framework for the calculations used in this script. 
# Some packages (e.g., datetime) are included in order to speed up calculations and simplify code.
#import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#from datetime import datetime
#import os # os is used with re to find name matches
#import re # see os
#import xarray as xr
import netCDF4 as nc
#from time import strftime
import timeit

#========== IMPORT INPUT AND FUNCTIONS FROM MODULES ===================================================================
import pygem_input as input
import pygemfxns_modelsetup as modelsetup
import pygemfxns_climate as climate
import pygemfxns_massbalance as massbalance
import pygemfxns_output as output

#%%======== DEVELOPER'S TO-DO LIST ====================================================================================
# > Output log file, i.e., file that states input parameters, date of model run, model options selected, 
#   and any errors that may have come up (e.g., precipitation corrected because negative value, etc.)

# ===== STEP ONE: Select glaciers included in model run ===============================================================
timestart_step1 = timeit.default_timer()
if input.option_glacier_selection == 1:
    # RGI glacier attributes
    main_glac_rgi = modelsetup.selectglaciersrgitable()
elif input.option_glacier_selection == 2:
    print('\n\tMODEL ERROR (selectglaciersrgi): this option to use shapefiles to select glaciers has not been coded '
          '\n\tyet. Please choose an option that exists. Exiting model run.\n')
    exit()
else:
    # Should add options to make regions consistent with Brun et al. (2017), which used ASTER DEMs to get mass 
    # balance of 92% of the HMA glaciers.
    print('\n\tModel Error (selectglaciersrgi): please choose an option that exists for selecting glaciers.'
          '\n\tExiting model run.\n')
    exit()
timeelapsed_step1 = timeit.default_timer() - timestart_step1
print('Step 1 time:', timeelapsed_step1, "s\n")

#%%=== STEP TWO: HYPSOMETRY, ICE THICKNESS, MODEL TIME FRAME, SURFACE TYPE ============================================
timestart_step2 = timeit.default_timer()
# Glacier hypsometry [km**2], total area
main_glac_hyps = modelsetup.import_Husstable(main_glac_rgi, input.rgi_regionsO1, input.hyps_filepath, 
                                             input.hyps_filedict, input.indexname, input.hyps_colsdrop)
# Ice thickness [m], average
main_glac_icethickness = modelsetup.import_Husstable(main_glac_rgi, input.rgi_regionsO1, input.thickness_filepath, 
                                                 input.thickness_filedict, input.indexname, input.thickness_colsdrop)
# Width [km], average
main_glac_width = modelsetup.import_Husstable(main_glac_rgi, input.rgi_regionsO1, input.width_filepath, 
                                              input.width_filedict, input.indexname, input.width_colsdrop)
# Add volume [km**3] and mean elevation [m a.s.l.] to the main glaciers table
main_glac_rgi['Volume'], main_glac_rgi['Zmean'] = modelsetup.hypsometrystats(main_glac_hyps, main_glac_icethickness)
# Model time frame
dates_table, start_date, end_date, monthly_columns, annual_columns, annual_divisor = modelsetup.datesmodelrun()
# Initial surface type
main_glac_surftypeinit = modelsetup.surfacetypeglacinitial(main_glac_rgi, main_glac_hyps)
# Print time elapsed
timeelapsed_step2 = timeit.default_timer() - timestart_step2
print('Step 2 time:', timeelapsed_step2, "s\n")

#%%=== STEP THREE: IMPORT CLIMATE DATA ================================================================================
timestart_step3 = timeit.default_timer()
if input.option_gcm_downscale == 1:
    # Air Temperature [degC] and GCM dates
    gcm_glac_temp, gcm_time_series = climate.importGCMvarnearestneighbor_xarray(
            input.gcm_temp_filename, input.gcm_temp_varname, main_glac_rgi, dates_table, start_date, end_date)
    # Precipitation [m] and GCM dates
    gcm_glac_prec, gcm_time_series = climate.importGCMvarnearestneighbor_xarray(
            input.gcm_prec_filename, input.gcm_prec_varname, main_glac_rgi, dates_table, start_date, end_date)
    # Elevation [m a.s.l] associated with air temperature data
    gcm_glac_elev = climate.importGCMfxnearestneighbor_xarray(
            input.gcm_elev_filename, input.gcm_elev_varname, main_glac_rgi)
else:
    print('\n\tModel Error: please choose an option that exists for downscaling climate data. Exiting model run now.\n')
    exit()
# Add GCM time series to the dates_table
dates_table['date_gcm'] = gcm_time_series
# Print time elapsed
timeelapsed_step3 = timeit.default_timer() - timestart_step3
print('Step 3 time:', timeelapsed_step3, "s\n")

#%%=== STEP FOUR: MASS BALANCE CALCULATIONS ===========================================================================
timestart_step4 = timeit.default_timer()

# Insert regional loop here if want to do all regions at the same time.  Separate netcdf files will be generated for
#  each loop to reduce file size and make files easier to read/share
regionO1_number = input.rgi_regionsO1[0]
# Create output netcdf file
output.netcdfcreate(regionO1_number, main_glac_hyps, dates_table, annual_columns)

# CREATE A SEPARATE OUTPUT FOR CALIBRATION with only data relevant to calibration
#   - annual glacier-wide massbal, area, ice thickness, snowline

#for glac in range(main_glac_rgi.shape[0]):
for glac in [0]:
    # Downscale the gcm temperature [degC] to each bin
    glac_bin_temp = massbalance.downscaletemp2bins(main_glac_rgi, main_glac_hyps, gcm_glac_temp, gcm_glac_elev, glac)
    # Downscale the gcm precipitation [m] to each bin (includes solid and liquid precipitation)
    glac_bin_precsnow = massbalance.downscaleprec2bins(main_glac_rgi, main_glac_hyps, gcm_glac_prec, gcm_glac_elev,glac)
    # Compute accumulation [m w.e.] and precipitation [m] for each bin
    glac_bin_prec, glac_bin_acc = massbalance.accumulationbins(glac_bin_temp, glac_bin_precsnow)
    # Compute potential refreeze [m w.e.] for each bin
    glac_bin_refreezepotential = massbalance.refreezepotentialbins(glac_bin_temp, dates_table)
    # Set initial surface type for first timestep [0=off-glacier, 1=ice, 2=snow, 3=firn, 4=debris]
    surfacetype = main_glac_surftypeinit.iloc[glac,:].values.copy()
    # Create surface type DDF dictionary (manipulate this function for calibration or for each glacier)
    surfacetype_ddf_dict = modelsetup.surfacetypeDDFdict()
    

    # List input matrices to simplify creating a mass balance function:
    #  - glac_bin_temp
    #  - glac_bin_acc
    #  - glac_bin_refreezepotential
    #  - surfacetype
    #  - surfacetype_ddf_dict
    #  - dayspermonth
    #  - main_glac_hyps
    # Variables to export with function
    glac_bin_refreeze = np.zeros(glac_bin_temp.shape)
    glac_bin_melt = np.zeros(glac_bin_temp.shape)
    glac_bin_meltsnow = np.zeros(glac_bin_temp.shape)
    glac_bin_meltrefreeze = np.zeros(glac_bin_temp.shape)
    glac_bin_meltglac = np.zeros(glac_bin_temp.shape)
    glac_bin_frontalablation = np.zeros(glac_bin_temp.shape)
    glac_bin_snowpack = np.zeros(glac_bin_temp.shape)
    glac_bin_massbalclim = np.zeros(glac_bin_temp.shape)
    glac_bin_massbalclim_annual = np.zeros((glac_bin_temp.shape[0],annual_columns.shape[0]))
    glac_bin_surfacetype_annual = np.zeros((glac_bin_temp.shape[0],annual_columns.shape[0]))
    glac_bin_icethickness_annual = np.zeros((glac_bin_temp.shape[0], annual_columns.shape[0] + 1))
    glac_bin_area_annual = np.zeros((glac_bin_temp.shape[0], annual_columns.shape[0] + 1))
    
    # Local variables used within the function
    snowpack_remaining = np.zeros(glac_bin_temp.shape[0])
    dayspermonth = dates_table['daysinmonth'].values
    surfacetype_ddf = np.zeros(glac_bin_temp.shape[0])
    refreeze_potential = np.zeros(glac_bin_temp.shape[0])
    elev_bins = main_glac_hyps.columns.values
    glacier_area_t0 = main_glac_hyps.iloc[glac,:].values.astype(float)
    # Inclusion of ice thickness and width, i.e., loading the values may be only required for Huss mass redistribution!
    icethickness_t0 = main_glac_icethickness.iloc[glac,:].values.astype(float)
    width_t0 = main_glac_width.iloc[glac,:].values.astype(float)
    if input.option_adjusttemp_surfelev == 1:
        # ice thickness initial is used to adjust temps to changes in surface elevation
        icethickness_adjusttemp = icethickness_t0.copy()
        icethickness_adjusttemp[0:icethickness_adjusttemp.nonzero()[0][0]] = (
                icethickness_adjusttemp[icethickness_adjusttemp.nonzero()[0][0]])
        #  bins that advance need to have an initial ice thickness; otherwise, the temp adjustment will be based on ice
        #  thickness - 0, which is wrong  Since advancing bins take the thickness of the previous bin, set the initial 
        #  ice thickness of all bins below the terminus to the ice thickness at the terminus.
    
    # Enter loop for each timestep (required to allow for snow accumulation which may alter surface type)
    for step in range(glac_bin_temp.shape[1]):
#    for step in range(0,26):
#    for step in range(0,12):
        
        # Option to adjust air temperature based on changes in surface elevation
        if input.option_adjusttemp_surfelev == 1:
            # Adjust the air temperature
            glac_bin_temp[:,step] = glac_bin_temp[:,step] + input.lr_glac * (icethickness_t0 - icethickness_adjusttemp)
            #  T_air = T+air + lr_glac * (icethickness_present - icethickness_initial)
            # Adjust refreeze as well
            #  refreeze option 2 uses annual temps, so only do this at the start of each year (step % annual_divisor)
            if (input.option_refreezing == 2) & (step % annual_divisor == 0):
                glac_bin_refreezepotential[:,step:step+annual_divisor] = massbalance.refreezepotentialbins(
                        glac_bin_temp[:,step:step+annual_divisor], dates_table.iloc[step:step+annual_divisor,:])
        # Remove input that is off-glacier (required for each timestep as glacier extent may vary over time)
        glac_bin_temp[surfacetype==0,step] = 0
        glac_bin_acc[surfacetype==0,step] = 0
        glac_bin_refreezepotential[surfacetype==0,step] = 0        
        # Compute the snow depth and melt for each bin...
        # Snow depth / 'snowpack' [m w.e.] = snow remaining + new snow
        glac_bin_snowpack[:,step] = snowpack_remaining + glac_bin_acc[:,step]
        # Available energy for melt [degC day]    
        melt_energy_available = glac_bin_temp[:,step]*dayspermonth[step]
        melt_energy_available[melt_energy_available < 0] = 0
        # Snow melt [m w.e.]
        glac_bin_meltsnow[:,step] = surfacetype_ddf_dict[2] * melt_energy_available
        # snow melt cannot exceed the snow depth
        glac_bin_meltsnow[glac_bin_meltsnow[:,step] > glac_bin_snowpack[:,step], step] = (
                glac_bin_snowpack[glac_bin_meltsnow[:,step] > glac_bin_snowpack[:,step], step])
        # Energy remaining after snow melt [degC day]
        melt_energy_available = melt_energy_available - glac_bin_meltsnow[:,step] / surfacetype_ddf_dict[2]
        # remove low values of energy available cause by rounding errors in the step above (e.g., less than 10**-12)
        melt_energy_available[abs(melt_energy_available) < input.tolerance] = 0
        # Compute the refreeze, refreeze melt, and any changes to the snow depth...
        # Refreeze potential [m w.e.]
        #  timing of refreeze potential will vary with the method, e.g., annual air temperature approach updates 
        #  annually vs heat conduction approach which updates monthly; hence, check if refreeze is being udpated
        if glac_bin_refreezepotential[:,step].max() > 0:
            refreeze_potential = glac_bin_refreezepotential[:,step]
        # Refreeze [m w.e.]
        #  refreeze cannot exceed the amount of snow melt, since it needs a source (accumulation zone modified below)
        glac_bin_refreeze[:,step] = glac_bin_meltsnow[:,step]
        # refreeze cannot exceed refreeze potential
        glac_bin_refreeze[glac_bin_refreeze[:,step] > refreeze_potential, step] = (
                refreeze_potential[glac_bin_refreeze[:,step] > refreeze_potential])
        glac_bin_refreeze[abs(glac_bin_refreeze[:,step]) < input.tolerance, step] = 0
        # Refreeze melt [m w.e.]
        glac_bin_meltrefreeze[:,step] = surfacetype_ddf_dict[2] * melt_energy_available
        # refreeze melt cannot exceed the refreeze
        glac_bin_meltrefreeze[glac_bin_meltrefreeze[:,step] > glac_bin_refreeze[:,step], step] = (
                glac_bin_refreeze[glac_bin_meltrefreeze[:,step] > glac_bin_refreeze[:,step], step])
        # Energy remaining after refreeze melt [degC day]
        melt_energy_available = melt_energy_available - glac_bin_meltrefreeze[:,step] / surfacetype_ddf_dict[2]
        # remove low values of energy available cause by rounding errors
        melt_energy_available[abs(melt_energy_available) < input.tolerance] = 0
        # Snow remaining [m w.e.]
        snowpack_remaining = (glac_bin_snowpack[:,step] + glac_bin_refreeze[:,step] - glac_bin_meltsnow[:,step] - 
                               glac_bin_meltrefreeze[:,step])
        snowpack_remaining[abs(snowpack_remaining) < input.tolerance] = 0
        # Compute any remaining melt and any additional refreeze in the accumulation zone...
        # DDF based on surface type [m w.e. degC-1 day-1]
        for surfacetype_idx in surfacetype_ddf_dict: 
            surfacetype_ddf[surfacetype == surfacetype_idx] = surfacetype_ddf_dict[surfacetype_idx]
        # Glacier melt [m w.e.] based on remaining energy
        glac_bin_meltglac[:,step] = surfacetype_ddf * melt_energy_available
        # Energy remaining after glacier surface melt [degC day]
        #  must specify on-glacier values, otherwise this will divide by zero and cause an error
        melt_energy_available[surfacetype != 0] = (melt_energy_available[surfacetype != 0] - 
                             glac_bin_meltglac[surfacetype != 0, step] / surfacetype_ddf[surfacetype != 0])
        # remove low values of energy available cause by rounding errors
        melt_energy_available[abs(melt_energy_available) < input.tolerance] = 0
        # Additional refreeze in the accumulation area [m w.e.]
        #  refreeze in accumulation zone = refreeze of snow + refreeze of underlying snow/firn
        glac_bin_refreeze[(surfacetype == 2) | (surfacetype == 3), step] = (
                glac_bin_refreeze[(surfacetype == 2) | (surfacetype == 3), step] +
                glac_bin_melt[(surfacetype == 2) | (surfacetype == 3), step])
        #  ALTERNATIVE CALCULATION: use ELA and reference into the bins - this requires the ELA and bin size such that
        #  the proper row can be referenced (this would not need to be updated assuming range of bins doesn't change.
        #  This may be an improvement, since this will need to be updated if more surface types are added in the future.
        # refreeze cannot exceed refreeze potential
        glac_bin_refreeze[glac_bin_refreeze[:,step] > refreeze_potential, step] = (
                refreeze_potential[glac_bin_refreeze[:,step] > refreeze_potential])
        # update refreeze potential
        refreeze_potential = refreeze_potential - glac_bin_refreeze[:,step]
        refreeze_potential[abs(refreeze_potential) < input.tolerance] = 0
        # Total melt (snow + refreeze + glacier)
        glac_bin_melt[:,step] = glac_bin_meltglac[:,step] + glac_bin_meltrefreeze[:,step] + glac_bin_meltsnow[:,step]
        # Climatic mass balance [m w.e.]
        glac_bin_massbalclim[:,step] = glac_bin_acc[:,step] + glac_bin_refreeze[:,step] - glac_bin_melt[:,step]
        #  climatic mass balance = accumulation + refreeze - melt
        
        # Compute frontal ablation
        if main_glac_rgi.loc[glac,'TermType'] != 0:
            print('Need to code frontal ablation: includes changes to mass redistribution (uses climatic mass balance)')
            # FRONTAL ABLATION IS CALCULATED ANNUALLY IN HUSS AND HOCK (2015)
            # How should frontal ablation pair with geometry changes?
            #  - track the length of the last bin and have the calving losses control the bin length after mass 
            #    redistribution
            #  - the ice thickness will be determined by the mass redistribution
            # Note: output functions calculate total mass balance assuming frontal ablation is a positive value that is 
            #       then subtracted from the climatic mass balance.
        
        # ENTER ANNUAL LOOP
        #  at the end of each year, update glacier characteristics (surface type, length, area, volume)
        if (step + 1) % annual_divisor == 0:
            # % gives the remainder; since step starts at 0, add 1 such that this switches at end of year
            # Index year
            year_index = int(step/annual_divisor)
            # for first year, need to record glacier area [km**2] and ice thickness [m ice]
            if year_index == 0:
                glac_bin_area_annual[:,year_index] = main_glac_hyps.iloc[glac,:].values.astype(float)
                glac_bin_icethickness_annual[:,year_index] = main_glac_icethickness.iloc[glac,:].values.astype(float)
            # Annual climatic mass balance [m w.e.]
            glac_bin_massbalclim_annual[:,year_index] = glac_bin_massbalclim[:,year_index*annual_divisor:step+1].sum(1)
            #  year_index*annual_divisor is initial step of the given year; step + 1 is final step of the given year
            
            ###### SURFACE TYPE (convert to function) #####
            glac_bin_surfacetype_annual[:,year_index] = surfacetype
            # Compute the surface type for each bin
            #  Next year's surface type is based on the bin's average annual climatic mass balance over the last 5
            #  years.  If less than 5 years, then use the average of the existing years.
            if year_index < 5:
                # Calculate average annual climatic mass balance since run began
                massbal_clim_mwe_runningavg = glac_bin_massbalclim_annual[:,0:year_index+1].mean(1)
            else:
                massbal_clim_mwe_runningavg = glac_bin_massbalclim_annual[:,year_index-4:year_index+1].mean(1)
            # If the average annual specific climatic mass balance is negative, then the surface type is ice (or debris)
            surfacetype[(surfacetype!=0) & (glac_bin_massbalclim_annual[:,year_index]<=0)] = 1
            # If the average annual specific climatic mass balance is positive, then the surface type is snow (or firn)
            surfacetype[(surfacetype!=0) & (glac_bin_massbalclim_annual[:,year_index]>0)] = 2
            # Apply surface type model options
            # If firn surface type option is included, then snow is changed to firn
            if input.option_surfacetype_firn == 1:
                surfacetype[surfacetype == 2] = 3
            if input.option_surfacetype_debris == 1:
                print('Need to code the model to include debris.  Please choose an option that currently exists.\n'
                      'Exiting the model run.')
                exit()
            
            
            # Glacier geometry change is dependent on whether model is being calibrated (option_calibration = 1) or not
            if input.option_calibration == 0:
                # Apply glacier geometry changes
                glacier_area_t1, icethickness_t1 = massbalance.massredistributionHuss(glacier_area_t0, icethickness_t0, 
                                                                                      width_t0, 
                                                                                      glac_bin_massbalclim_annual, 
                                                                                      year_index)
                # Update surface type for bins that have retreated or advanced
                surfacetype[glacier_area_t0 == 0] = 0
                surfacetype[(surfacetype == 0) & (glacier_area_t1 != 0)] = surfacetype[glacier_area_t0.nonzero()[0][0]]
                # Record and update ice thickness and glacier area for next year
                if year_index < input.spinupyears:
                    # For spinup years, glacier area and volume are constant
                    glac_bin_icethickness_annual[:,year_index + 1] = icethickness_t0
                    glac_bin_area_annual[:,year_index + 1] = glacier_area_t0
                else:
                    # Record ice thickness [m ice] and glacier area [km**2]
                    glac_bin_icethickness_annual[:,year_index + 1] = icethickness_t1
                    glac_bin_area_annual[:,year_index + 1] = glacier_area_t1
                    # Update glacier area [km**2] and ice thickness [m ice]
                    icethickness_t0 = icethickness_t1.copy()
                    glacier_area_t0 = glacier_area_t1.copy()
        
                
    
        # NOTE: 
        # If bin retreats and then advances over a discontinuous section of glacier, then how is this avoided in
        #  future time steps?  Is this an issue?
            
        # Options to add:
        # - Refreeze via heat conduction
        # - Volume-Area, Volume-Length scaling

    # Record variables from output package here - need to be in glacier loop since the variables will be overwritten 
#    output.netcdfwrite(regionO1_number, glac, main_glac_rgi, elev_bins, glac_bin_temp, glac_bin_prec, glac_bin_acc, 
#                       glac_bin_refreeze, glac_bin_snowpack, glac_bin_melt, glac_bin_frontalablation, 
#                       glac_bin_massbalclim, glac_bin_massbalclim_annual, glac_bin_area_annual, 
#                       glac_bin_icethickness_annual, glac_bin_surfacetype_annual)
    #  WILL NEED TO UPDATE HOW THE GLACIER PARAMETERS ARE STRUCTURED ONCE THEY ARE CALIBRATED FOR EACH GLACIER

timeelapsed_step4 = timeit.default_timer() - timestart_step4
print('Step 4 time:', timeelapsed_step4, "s\n")

#%%=== STEP FIVE: DATA ANALYSIS / OUTPUT ==============================================================================
#netcdf_output = nc.Dataset('../Output/PyGEM_output_rgiregion15_20180202.nc', 'r+')
#netcdf_output.close()

