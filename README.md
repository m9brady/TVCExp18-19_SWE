# TVC Experiment 2018/19 - SWE retrieval algorithm

This repository contains the techniques and code referenced in the following publication:


>  Montpetit, B., Meloche, J., Vionnet, V., Derksen, C., Woolley, G., Leroux, N. R., Siqueira, P., Adam, J. M., and Brady, M. : Retrieving Snow Water Equivalent from airborne Ku-band data: The Trail Valley Creek 2018/19 Snow Experiment, EGUsphere [preprint], link TBD, 2025.


Open-Access Publication (Preprint): [![Static Badge](https://img.shields.io/badge/The_Cryosphere-blue)](https://doi.org/10.5194/egusphere-2024-651)

Open-Access Dataset:  
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10794207.svg)](https://doi.org/10.5281/zenodo.10794207)  
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10794918.svg)](https://doi.org/10.5281/zenodo.10794918)   


## Abstract

Snow is an important fresh water resource that impacts health and well-being of communities, the economy, and sustains ecosystems of the cryosphere. This is why there is a need for a spaceborne earth observation mission to monitor global snow conditions. Environment and Climate Change Canada, in partnership with the Canadian Space Agency, is developing a new Ku-band synthetic aperture radar mission to retrieve snow water equivalent (SWE) at a nominal resolution of 500~m, and weekly coverage of the cryosphere. Here, we present the concept of the SWE retrieval algorithm for this proposed satellite mission. It is shown that by combining a priori knowledge of snow conditions from a land surface model, like the Canadian Soil Vegetation Snow version 2 model (SVS-2), in a Markov Chain Monte Carlo model, we can retrieve SWE with an RMSE of 15.8~mm (16.4~$\%$) with an uncertainty of 34.8~mm (37.7~$\%$). To achieve this accuracy, a larger uncertainty to the a priori grain size estimation is required, since this variable is known to be underestimated within SVS-2, and is also known to have a considerable impact on the microwave scattering properties of snow. It is also shown that by adding four observations from different incidence angles, improves the accuracy of the SWE retrieval because these observations are sensitive to different scattering mechanisms of the snowpack. These results validate the mission concept of the proposed Canadian satellite mission.

<p align="center">
    <img src="Figures/f01.png">
</p>

<p align="center">
    <i>Figure 1 from <a href="https://doi.org/10.5194/egusphere-2024-651">Montpetit et al. (Preprint)</a>: Sites sampled during the January campaign of the TVC 2018/19 experiment. Squares correspond to a 100 m x 100 m around the central surveyed snowpit (see Section 2.2). Background images are two overlapped UMASS Ku-Band radar images corresponding to two different flight passes acquired November 14, 2018. The black grid lines represents the extent of a 2.5 km grid, similar to the Canadian High Resolution Deterministic Prediction System grid (see Section 2.3).</i>
</p>

## Environment Configuration

Use [miniconda](https://docs.conda.io/projects/miniconda/en/latest/), [mamba](https://mamba.readthedocs.io/en/latest/) or [anaconda](https://www.anaconda.com/download) to recreate the runtime environment:


```
conda env create -n tvc1819 -f environment.yml
conda activate tvc1819
```

The `tvc1819` environment installs the Snow Microwave Radiative Transfer Model (SMRT) version 1.2.4 (released 2024/01/18). If you would like to use a more recent version, then with the environment activated you can follow the installation instructions from [G. Picard](https://github.com/ghislainp) to install the latest stable SMRT release: [SMRT install instructions](https://github.com/smrt-model/smrt?tab=readme-ov-file#quick-installation)

> **Warning** 
> The provided environment.yml file was generated on Linux and may behave differently on Windows or Mac systems.

## Data Preparation

To download the datasets used by the notebooks, use the following links:

- [Zenodo: TVC Experiment 2018/19: Snow Field Measurements](https://doi.org/10.5281/zenodo.10794207)
  - Zip file containing all the files under the `Site` subdirectory
- [Zenodo: TVC Experiment 2018/19: UMass Airborne Ku-Band SAR data](https://doi.org/10.5281/zenodo.10794918)
  - `UMass_TVC18-19_DB.geojson`
- [Zenodo: TVC Experiment 2018/19: TerraSAR-X backscatter data](https://doi.org/10.5281/zenodo.10794868)
  - `SoilRough_ALS2018_TVC18-19.json`

and store the data as shown:

```
Data
├── UMass_TVC18-19_DB.geojson
├── SoilRough_ALS2018_TVC18-19.json
```

## Exploring the Notebooks

After setting up the environment and data, you may wish to look first at the Table of Contents in [the index notebook](./index.ipynb) to discover which parts of the code interest you. In order to launch the Table of Contents notebook on your local system, use the following command while inside the activated `tvc1819` environment:

```
jupyter notebook index.ipynb
```
