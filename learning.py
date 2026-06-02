import xarray as xr
import numpy as np
import pandas as pd

ds = xr.open_dataset(r"E:\Job Important Documents\Projects\FloatChat\Float_Data\01Jan\20250101_prof.nc")
ds2= xr.open_dataset(r"E:\Job Important Documents\Projects\FloatChat\Float_Data\01Jan\20250102_prof.nc")
# print(ds)
# print(ds.dims)
# print(ds.data_vars)

n_profiles = ds.dims["N_PROF"]
print(f"Number of profiles: {n_profiles}")

print(ds) 
