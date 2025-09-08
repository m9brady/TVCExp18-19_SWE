import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import xarray as xr
from datetime import datetime

# smrt package installed from pip
from smrt.core.globalconstants import DENSITY_OF_ICE
from smrt import sensor_list, make_model, make_snowpack, make_interface
from smrt.emmodel import iba
from smrt.substrate.reflector_backscatter import make_reflector


def import_crocus(file_path, str_year_begin):
    """Function docstring"""
    mod = xr.open_dataset(file_path)
    df = mod[['SNODEN_ML','SNOMA_ML','TSNOW_ML','SNODOPT_ML','SNODP']].to_dataframe().dropna() 
    # SNODEN_ML: densite des couches
    # SNOMA_ML: SWE des couches
    # TSNOW_ML: T des couches
    # SNODOPT_ML: diametre optique des couches
    # SNODP: hauteur totale du snowpack
    # filter at 5 seasons of beginin 
    str_begin = str_year_begin + '-10-01'
    oct01 = datetime.strptime(str_begin, '%Y-%m-%d')
    df = df.loc[oct01:,:]
    df['thickness'] = df[['SNODEN_ML','SNOMA_ML']].apply(lambda x : x[1] / x[0], axis = 1) 
    df['ssa'] = df['SNODOPT_ML'].apply(lambda x: 6/( x * 917) if x>0 else 0)
    # filter out low snowdepth and small snow layers
    df = df[(df['SNODP'] > 0.10) & (df['thickness'] > 0.005)]
    dates = df.groupby(level = 'time').mean().index.get_level_values(0)
    # add height to dataframe
    df['height'] = np.nan
    for date in dates:
        df_temp = df.loc[date, :]
        df.loc[date, 'height'] = np.cumsum(df_temp['thickness'].values[::-1])[::-1]
    return df, dates


def run_colP(df, dates, method, layer_type, model = 'iba'):
    """Based on the provided layer_type, use SMRT to calculate backscatter estimate"""
    if layer_type == 'two':
        snow = [build_snow(two_layer(df.loc[date,:], method = method)) for date in dates]
        swe = [(two_layer(df.loc[date,:], method = method)['SNODEN_ML'] * two_layer(df.loc[date,:], method = method)['thickness']).sum() for date in dates]
        # calculate backscatter
        result = run_simu(snow, model = model)
        sig = result.sigmaVV().values
        return sig, swe
    if layer_type == 'two_k':
        snow = [build_snow(two_layer_k(df.loc[date,:], method = method)) for date in dates]
        swe = [(two_layer_k(df.loc[date,:], method = method)['SNODEN_ML'] * two_layer_k(df.loc[date,:], method = method)['thickness']).sum() for date in dates]
        # calculate backscatter
        result = run_simu(snow, model = model)
        sig = result.sigmaVV().values
        return sig, swe
    if layer_type == 'three':
        snow = [build_snow(three_layer(df.loc[date,:], method = method)) for date in dates]
        swe = [(three_layer(df.loc[date,:], method = method)['SNODEN_ML'] * three_layer(df.loc[date,:], method = method)['thickness']).sum() for date in dates]
        # calculate backscatter
        result = run_simu(snow, model = model)
        sig = result.sigmaVV().values
        return sig, swe
    if layer_type == 'three_k':
        snow = [build_snow(three_layer_k(df.loc[date,:], method = method)) for date in dates]
        swe = [(three_layer_k(df.loc[date,:], method = method)['SNODEN_ML'] * three_layer_k(df.loc[date,:], method = method)['thickness']).sum() for date in dates]  
        #calculate backscatter
        result = run_simu(snow, model = model)
        sig = result.sigmaVV().values
        return sig, swe


def debye_eqn(ssa, density):
    """Function docstring"""
    return 4 * (1 - density / DENSITY_OF_ICE) / (ssa * DENSITY_OF_ICE)  


def build_snow(snow_df, transparent = False, transparent_nosurf = False):
    """Function docstring"""
    t_soil = 265
    sub = make_reflector(temperature=t_soil, specular_reflection=0, 
                              backscattering_coefficient={'VV' : 0, 'HH' : 0})
    # sig_soil = 0.02
    # lc_soil = 0.3
    # eps = complex(3.5, 0.1)
    # mss=2*(sig_soil/lc_soil)**2
    # sub = make_soil('geometrical_optics', 
    #                 permittivity_model = eps, 
    #                 mean_square_slope=mss, 
    #                 temperature = t_soil)
    # Creating the snowpack to simulate with the substrate
    if isinstance(snow_df['thickness'], np.floating):
        thickness = [snow_df['thickness']]
    else:
        thickness = snow_df['thickness']
    try:
        if transparent:
            sp = make_snowpack(thickness=thickness, 
                            microstructure_model='exponential',
                            density= snow_df['SNODEN_ML'],
                            temperature= snow_df['TSNOW_ML'],
                            corr_length = 0.75 * debye_eqn(snow_df['ssa'].values, snow_df['SNODEN_ML'].values),
                            substrate = sub)
            sp.interfaces = [make_interface('transparent') for inter in range(len(sp.interfaces))]
        elif transparent_nosurf:
            sp = make_snowpack(thickness=thickness, 
                            microstructure_model='exponential',
                            density= snow_df['SNODEN_ML'],
                            temperature= snow_df['TSNOW_ML'],
                            corr_length = 0.75 * debye_eqn(snow_df['ssa'].values, snow_df['SNODEN_ML'].values),
                            substrate = sub)
            sp.interfaces = [make_interface('transparent') for inter in range(len(sp.interfaces))]
            sp.interfaces[0] = make_interface('flat')
        else:  
            sp = make_snowpack(thickness=thickness, 
                            microstructure_model='exponential',
                            density= snow_df['SNODEN_ML'],
                            temperature= snow_df['TSNOW_ML'],
                            corr_length = 0.75 * debye_eqn(snow_df['ssa'].values, snow_df['SNODEN_ML'].values),
                            substrate = sub)
        return sp
    except:
        print(snow_df)


def run_simu(sp, model = 'iba', diag_method = 'eig', freq = 17.5e9):
    """Function docstring"""
    # Modeling theories to use in SMRT
    if model == 'iba':
        model = make_model("iba", "dort", rtsolver_options=dict(error_handling='nan',
                                                                diagonalization_method=diag_method))
    if model == 'iba_inv':
        model = make_model("iba", "dort", emmodel_options=dict(dense_snow_correction="auto"),
                                          rtsolver_options=dict(error_handling='nan', 
                                                                diagonalization_method=diag_method))
    if model == 'symsce':
        model = make_model("symsce_torquato21", "dort", rtsolver_options=dict(error_handling='nan',
                                                                              diagonalization_method=diag_method))
    sensor  = sensor_list.active(freq, 35)
    result = model.run(sensor, sp, parallel_computation=True)
    return result

def compute_ke(snow_df, freq = 17.5e9):
    """Function docstring"""
    # Creating the snowpack to simulate with the substrate
    if isinstance(snow_df['thickness'], np.floating):
        thickness = [snow_df['thickness']]
    else:
        thickness = snow_df['thickness']
    sp = make_snowpack(thickness=thickness, 
                        microstructure_model='exponential',
                        density= snow_df['SNODEN_ML'],
                        temperature= snow_df['TSNOW_ML'],
                        corr_length = debye_eqn(snow_df['ssa'].values, snow_df['SNODEN_ML'].values))
    # create sensor
    sensor  = sensor_list.active(freq, 35)
    # get ks from IBA class
    ks = np.array([iba.IBA(sensor, layer, dense_snow_correction='auto')._ks for layer in sp.layers])
    ka = np.array([iba.IBA(sensor, layer, dense_snow_correction='auto').ka for layer in sp.layers])
    ke = ks + ka
    return ke

def avg_snow_sum_thick(snow_df, method = 'thick', freq = 17.5e9):
    """Function docstring"""
    if method not in ['thick', 'thick-ke', 'thick-ke-density']:
        raise NotImplementedError("Requested method '{method}' not implemented. Choose one of ['thick', 'thick-ke', 'thick-ke-density']")
    thick = snow_df['thickness'].sum()
    if method == 'thick':
        snow_mean = snow_df.apply(lambda x: np.average(x, weights=snow_df['thickness'].values), axis=0)
        snow_mean['thickness'] = thick
    elif method == 'thick-ke':
        snow_df['ke'] = compute_ke(snow_df, freq=freq)
        snow_mean = snow_df.apply(lambda x: np.average(x, weights=snow_df['thickness'].values * snow_df['ke'].values), axis=0)
        snow_mean['thickness'] = thick
    elif method == 'thick-ke-density':
        snow_df['ke'] = compute_ke(snow_df, freq=freq)
        df_copy = snow_df.copy()
        density_temp = np.average(df_copy['SNODEN_ML'], weights=snow_df['thickness'].values )
        snow_mean = snow_df.apply(lambda x: np.average(x, weights=snow_df['thickness'].values * snow_df['ke'].values, axis=0))
        snow_mean['thickness'] = thick
        snow_mean['SNODEN_ML'] = density_temp
    return snow_mean


def two_layer(snow_df, method = 'thick'):
    """Function docstring"""
    # get norm height
    snow_df['norm_h'] = snow_df['height'] / snow_df['thickness'].sum()
    # split by third and average
    snow_1 = avg_snow_sum_thick(snow_df[snow_df['norm_h'] >= 0.5], method = method)
    snow_2 = avg_snow_sum_thick(snow_df[snow_df['norm_h'] < 0.5], method = method) 
    return pd.DataFrame([df for df in [snow_1, snow_2] if not df.empty])


def two_layer_k(snow_df, method = 'thick'):
    """kmean cluster classification of two layer snowpack"""
    X = pd.DataFrame({ 'ke' : compute_ke(snow_df), 'height' : snow_df['height']})
    kmeans = KMeans(n_clusters=2, random_state=0, n_init="auto").fit(X)
    snow_df['label'] = kmeans.labels_
    df = snow_df.groupby('label', sort = False).apply(lambda x: avg_snow_sum_thick(x, method = method))
    return df


def three_layer(snow_df, method = 'thick'):
    """Function docstring"""
    # get norm height
    snow_df['norm_h'] = snow_df['height'] / snow_df['thickness'].sum()
    # split by third and average
    snow_1 = avg_snow_sum_thick(snow_df[snow_df['norm_h'] >= 0.66], method = method)
    # check if empty
    if not snow_df[(snow_df['norm_h'] <= 0.66) & (snow_df['norm_h'] >= 0.34)].empty:
        snow_2 = avg_snow_sum_thick(snow_df[(snow_df['norm_h'] <= 0.66) & (snow_df['norm_h'] >= 0.34)], method = method) 
    else:
        snow_2 = pd.DataFrame()
    # check if empty
    if not snow_df[snow_df['norm_h'] < 0.34].empty:
        snow_3 = avg_snow_sum_thick(snow_df[snow_df['norm_h'] < 0.34], method = method) 
    else: 
        snow_3 = pd.DataFrame()
    return pd.DataFrame([df for df in [snow_1, snow_2, snow_3] if not df.empty])


def three_layer_k(snow_df, method = 'thick', freq = 17.5e9):
    """kmean cluster classification of three layer snowpack"""
    X = pd.DataFrame({ 'ke' : compute_ke(snow_df, freq =freq),  'height' : snow_df['height']})
    kmeans = KMeans(n_clusters=3, random_state=0, n_init="auto").fit(X)
    snow_df['label'] = kmeans.labels_
    df = snow_df.groupby('label', sort = False).apply(lambda x: avg_snow_sum_thick(x, method = method, freq =freq))
    return df
