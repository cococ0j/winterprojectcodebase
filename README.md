# Instruction of SITS Pre-Processing Chain

## 1. Introduction
SITS Pre-processing chain achieves the serial pre-processing of satellite data including downloading, atmospheric correction and gap-filling for temporal data. It composes all three processes into one single command. At the present, it is mainly implemented for data of Victoria State from Sentinel-2 mission.

Every dependent package or software is listed in “Prerequisite” section. Before launch the chain, it is necessary to install and correctly configure all dependant packages and software. Modules of the chain is described in “Modules” section, which you could learn every parameter or option to launch the chain and functions of different modules. We also include some auxiliary files to help us configure the chain. They can be learnt from “Auxiliary files” section. At last, we give the main workflow of this processing chain and some example commands.

As the chain is still under developing, there are some limitations for the chain. We list all of them in “Limitation” section.

## 2. Prerequisite
### 2.1 Python Libraries

The chain requires the following Python libraries:

* argparse
* gdal,ogr
* config
* glob
* shutil
* osgeo
* collections
* numpy, pandas
* scipy
* osr
* random
* matplotlib
* subprocess
* filecmp
* gdal
* lxml

### 2.2 Install Sen2Cor 2.5.5

Please see [Section 3 of Sen2Cor Configuration and User Manual](https://step.esa.int/thirdparties/sen2cor/2.4.0/Sen2Cor_240_Documenation_PDF/S2-PDGS-MPC-L2A-SUM-V2.4.0.pdf)for more details.

**One important thing is you should add `L2A_Process` command into your searching path of your OS.**



### 2.3 Install IOTA2

#### 2.3.1DESCRIPTION OF REQUIREMENTS

Two scripts are provided: init_CentOS.sh and init_Ubuntu.sh.
All packages needed on CentOS or Ubuntu Linux system will be installed by the script. Administrator rights are required to execute it.

#### 2.3.2 LIST OF TOOLS AND SOFTWARE NEEDED TO BUILD iota2 CHAIN

Ask to administrator of system to install libraries and softwares listed below:

- git
- cmake
- c++
- zlib et zlib1g-dev
- python 2.7 et python-dev
- pip
- freeglut3-dev (paquet dev OpenGl)
- libX11-dev (paquet dev X11)
- libxext-dev (paquet dev des extensions X11)
- libxi-dev (paquet dev des extensions X11 input)
- boost (libboost-all-dev) 
- swig
- gsl et gsl-dev (paquet dev gsl)
- patch

#### 2.3.3 LIST OF TOOLS AND SOFTWARE NEEDED TO EXECUTE iota2 CHAIN

Following python packages are needed :

- pytz 
- python-dateutil

#### 2.3.4 BUILDING PROCESS DESCRIPTION

This chapter describe the building process of iota2 chain. All libraries and softwares require describe at previous chapter must be installed.
There are two building modes:

- The first one is based on source package download from Internet. The computer need intenet connexion to use this mode.
- The second one is based on an archive containing all source files.

The building process is divided into two steps:

- The first step is the download of all source files and archives :
  - Source files of OTB (Orfeo ToolBox)
  - Source files of CESBIO GapFilling
  - Source files of CESBIO iota2
- The second step is the compilation of all source files. This step is divide into two parts: the compilation of OTB dependencies and OTB itself, and the compilation of GapFilling and iota2 modules.

All these steps are automated in generation.sh script.
Be careful all compilation products will be installed in the directory where the script is executed. This could take a lot of disk space, until 5Gb.

```shell
$ ./generation.sh

Usage : ./generation.sh --compil --update --all
--update : download of source files only
--compil : compilation only
--all : download + compilation

module : OTB iota2

The script has two arguments. The first one, mandatory, could take 3 values:
--update: download and update all source files
--compil: build OTB and modules
--all: makes consecutively the two steps above.

The second argument, optional, can indicate two download or build only OTB or iota2 and GapFilling modules.

For a first installation, WITHOUT archive, use this command:
$ ./generation.sh --all

# For a fist installation, WITH archive, use this command:
$ ./generation.sh --compil
```

The download and building of OTB can take a lot of time, it can take several hours.

The script produces an archive: iota2_OTB-6.0.tar.gz which contains binaries and libraries generated.

#### 2.3.5 INSTALLATION PROCESS DESCRIPTION

This chapter describes installation process of iota2 chain and execution environment preparation.

Two cases can happen: You use the generated archive, which must be uncompressed in a directory. Or you directly use the directory where the building has been done.
You must create the environment variable $iota2_PATH which indicate the installation path.

```shell 
$ export iota2_PATH=/Path_to_installation_directory

# To uncompressed the archive:
$ cd iota2_PATH
$ tar –xzf iota2_OTB-6.0.tar.gz

# Environment setting script:
$ source prepare_env.sh

# On CNES cluster you must used this script:
$ source prepare_env_cluster.sh
```

If no error appear the environment of the chain is ready.

#### 2.3.6 Errors and Solutions

##### 2.3.6.1 GEOS installation. 

This seems more related to OTB installation:
https://gitlab.orfeo-toolbox.org/orfeotoolbox/otb/issues/1574
According to Guillaume Passero, the issue should have been fixed. 
We followed Jordi comment and changed the platform.h that is in the
following directory: OTB/build/GEOS/src/GEOS/include/geos/platform.h
We changed line 142 of this file by

```define ISNAN(x) std::isnan(x)```

##### 2.3.6.2 mpi4py package (>V3)

It requires the modification of IOTA2.py:

```python
MPI.pickle.dumps = dill.dumps
MPI.pickle.loads = dill.loads
MPI.pickle.init(dill.dumps, dill.loads)
```

## 3. Modules
### 3.1 sits_process_chain.py
This is the main Python script you will use to execute the whole processing chain. It is composed of all three pre-processing steps into one single command with following multiple options:

| Field |Option| Description | Mandatory ? | Condition | Example |
| :----------: | :--------: | :-----: | :----------: | :----------: | :----------: |
| list of tiles | -t| A list of tiles you are interested | mandatory |  | [54HYE,54HBV]<br />or<br />[54HYE, 54HBV] |
| start date|-d| The beginning  date of acquisition  data | mandatory | At this time, it should be after 2016-12-15, otherwise we should add more parameter because of peps. | 2018-04-01 |
|end date|-f| The closing  date of acquisition  data | mandatory |  | 2018-05-30 |
|write dir |-w|main path to store data| mandatory | Absolute path | /main/path/to/store/data |
|save l1c |--s1| Save l1c data or not, after processing | Default =TRUE | bolean value | --s1 False |
|save l2a |--s2| Save l2c data or not after processing | Default =TRUE | boolean value | --s2 True |
|L2A processor |--lp| Choose atmospheric correction processor | Default = sen2cor | sen2cor or MAJA | --lp sen2cor |
|Cloud covering lower boundary |--ll| Cloud covering lower boundary | Default = 0 | [0,100] | --ll 5 |
|Cloud covering upper boundary |--ul| Cloud covering upper boundary | Default = 95 | [lower boudary,100] | --up 95 |
|firstStep |--fs| Runing downloading step or not | Default = True | boolean value | --fs True |
|lastStep |--ls| Running gap-filling or not | Default = True | boolean value | --ls True |

### 3.2 peps_download.py
It is originally developed by [Olivier]( https://github.com/olivierhagolle/peps_download). Here, we made following modifications:

* Add tile option: users can choose tiles to download.
* Add cloud covering option:  users can choose data to download with given cloud covering.
* Set 2min re-try time for downloading data on TAPE

### 3.3 config_sen2cor.py
This python script allows you to configure atmospheric correction processor (perfomed by Sen2Cor). It can open and edit to set parameters using any text editor. IT IS IMPORTANT TO SAVE IT BEFORE YOU CLOSE.

Details of parameters are as following:

| Parameter         | Description                                                  |                            Value                             | Example                                     |
| ----------------- | ------------------------------------------------------------ | :----------------------------------------------------------: | ------------------------------------------- |
| Nr_Processes      | the number or processes you intend to operate in parallel    | Numbers  AUTO. If AUTO is chosen, the processor determines the number of processes automatically, using cpu_count() | <Nr_Processes>1</Nr_Processes>              |
| Aerosol_Type      | Aerosol Type                                                 |                    RURAL, MARITIME, AUTO                     | <Aerosol_Type>RURAL</Aerosol_Type>          |
| Mid_Latitude      | Mid Latitude                                                 |                     SUMMER, WINTER, AUTO                     | <Mid_Latitude>SUMMER</Mid_Latitude>         |
| Ozone_Content     | The atmospheric temperature profile and ozone content in Dobson Unit (DU) | -1: automatically choose the best approximate ozone from ozone lookup table<br>For midlatitude summer (MS) atmosphere:250, 290, 331 (standard MS), 370, 410, 450<br>For midlatitude winter (MW) atmosphere:250, 290, 330, 377 (standard MW), 420, 460 | <Ozone_Content>331</Ozone_Content>          |
| WV_Correction     |                                                              | 0: No WV correction, 1: only 940 nm bands, 2: only 1130 nm bands , 3: both regions used during wv retrieval,4: Thermal region | <WV_Correction>1</WV_Correction>            |
| VIS_Update_Mode   |                                                              |             0: constant, 1: variable visibility              | <VIS_Update_Mode>1</VIS_Update_Mode>        |
| WV_Watermask      |                                                              |      0: not replaced, 1: land-average, 2: line-average       | <WV_Watermask>1</WV_Watermask>              |
| Cirrus_Correction |                                                              | FALSE: no cirrus correction applied, TRUE: cirrus correction applied | <Cirrus_Correction>TRUE</Cirrus_Correction> |
| BRDF_Correction   |                                                              | 0: no BRDF correction, 1: , 2: ,11, 12, 22, 21: see IODD for explanation | <BRDF_Correction>1</BRDF_Correction>        |
| BRDF_Lower_Bound  |                                                              | In most cases, g=0.2 to 0.25 is adequate, in extreme cases of overcorrection g=0.1 should be applied | <BRDF_Lower_Bound>0.25</BRDF_Lower_Bound>   |

### 3.4 sen2cor_process.py
This Python script is the main file for Sen2Cor processing. 

### 3.5 extract_tempoal_distribution.py

This Python script helps you to plot cloud covering for L1C data you have downloaded.

It takes L1C data folder name as an input, and the outputs are as follows:

- a text file with all the acquisition dates in ascending order (format yyyymmdd); one date by line
- a bar chart with the acquisition date on the horizontal axis, and the estimated cloud cover in the vertical line. You may

The cloud covering is the 'Cloud_Coverage_Assessment' tag found in the xml file of each SAFE folder:
 <Cloud_Coverage_Assessment>86.49903571428571</Cloud_Coverage_Assessment>

Sample command:

```shell
python extractTempoalDistribution.py -i /Users/jibusi/Downloads/winterproject/data/Bendigo2 -o /Users/jibusi/Downloads/winterproject/data -p /Users/jibusi/Downloads/winterproject/data
```

## 4. Auxiliary files
| File name | Description | Example |
| -- | -- | -- |
|L2A_GIPP.xml|A copy of default Sen2cor configuration. |  |
| OzoneLUT.csv | Ozone history data for Victoria is original from [World Ozone and Ultraviolet Radiation Data Centre](https://woudc.org/home.php). We cleaned the raw data and convert it into CSV format. |  |
| peps.txt | Peps username and password. | your.email@address.fr top_secret |

## 5. Workflow and Examples
To excute the chain, it is required to follow two steps:

1. Configure and install all requited packages and software;
2. Go to project folder;
3. Modify config_sen2cor.py to set parameters for Sen2Cor;
4. Run sits_process_chain.py with appropriate parameters.

#### Command Example:

```shell
# Process two tiles (54HYE,54HBV) with default settings
python sits_process_chain.py -t [54HYE,54HBV] -d 2018-04-14 -f 2018-04-26 -w /Path/to/writing/directory/data/Test

# Process two tiles (54HYE,54HBV) with cloud covering [10,80] and without first step.
python sits_process_chain.py -t [54HYE,54HBV] -d 2018-04-14 -f 2018-04-26 -w /Path/to/writing/directory/data/Test --ll 10 --ul 80 --fs False 
```

#### One output sample structure is as following:

```bash
test_data
    ├── AUX
    │   ├── 20180714T213351.log
    │   ├── 20180714T213457.log
    │   ├── 20180714T215859.log
    │   ├── 20180714T223137.log
    │   ├── 20180714T231330.log
    │   ├── 20180714T231450.log
    │   ├── 20180715T001524.log
    │   ├── 20180715T002600.log
    │   ├── 20180715T002629.log
    │   ├── 20180715T002714.log
    │   ├── 20180715T002904.log
    │   ├── 20180715T003110.log
    │   ├── 20180717T204943.log
    │   ├── 20180717T205254.log
    │   ├── 20180717T205532.log
    │   ├── 20180717T212024.log
    │   ├── 20180717T212140.log
    │   ├── 20180722T210834.log
    │   ├── 20180722T211000.log
    │   └── L2A_GIPP.xml
    ├── L1C
    │   ├── T54HXE
    │   │   └── S2B_MSIL1C_20180411T002049_N0206_R116_T54HXE_20180411T014716.SAFE
    │   ├── T54HYE
    │   │   ├── S2A_MSIL1C_20180416T002101_N0206_R116_T54HYE_20180416T022552.SAFE
    │   │   ├── S2A_MSIL1C_20180426T002101_N0206_R116_T54HYE_20180426T014236.SAFE
    │   │   ├── S2A_MSIL1C_20180429T002711_N0206_R016_T54HYE_20180429T020327.SAFE
    │   │   ├── S2A_MSIL1C_20180506T002101_N0206_R116_T54HYE_20180506T014715.SAFE
    │   │   ├── S2A_MSIL1C_20180509T002711_N0206_R016_T54HYE_20180509T033541.SAFE
    │   │   ├── S2A_MSIL1C_20180516T002101_N0206_R116_T54HYE_20180516T014607.SAFE
    │   │   ├── S2A_MSIL1C_20180519T002711_N0206_R016_T54HYE_20180519T015836.SAFE
    │   │   ├── S2A_MSIL1C_20180526T002101_N0206_R116_T54HYE_20180526T014739.SAFE
    │   │   ├── S2A_MSIL1C_20180529T002711_N0206_R016_T54HYE_20180529T020042.SAFE
    │   │   ├── S2B_MSIL1C_20180401T002049_N0206_R116_T54HYE_20180401T015154.SAFE
    │   │   ├── S2B_MSIL1C_20180411T002049_N0206_R116_T54HYE_20180411T014716.SAFE
    │   │   ├── S2B_MSIL1C_20180424T002709_N0206_R016_T54HYE_20180424T020423.SAFE
    │   │   ├── S2B_MSIL1C_20180504T002709_N0206_R016_T54HYE_20180504T020239.SAFE
    │   │   ├── S2B_MSIL1C_20180511T002059_N0206_R116_T54HYE_20180511T015205.SAFE
    │   │   ├── S2B_MSIL1C_20180514T002709_N0206_R016_T54HYE_20180514T014806.SAFE
    │   │   ├── S2B_MSIL1C_20180521T002049_N0206_R116_T54HYE_20180521T032735.SAFE
    │   │   ├── S2B_MSIL1C_20180524T002709_N0206_R016_T54HYE_20180524T014647.SAFE
    │   │   └── S2B_MSIL1C_20180531T002049_N0206_R116_T54HYE_20180531T013551.SAFE
    │   └── T55HBV
    │       ├── S2A_MSIL1C_20180406T002051_N0206_R116_T55HBV_20180406T014755.SAFE
    │       ├── S2A_MSIL1C_20180409T002711_N0206_R016_T55HBV_20180409T021507.SAFE
    │       ├── S2A_MSIL1C_20180419T002711_N0206_R016_T55HBV_20180419T020033.SAFE
    │       ├── S2A_MSIL1C_20180426T002101_N0206_R116_T55HBV_20180426T014236.SAFE
    │       ├── S2A_MSIL1C_20180429T002711_N0206_R016_T55HBV_20180429T020327.SAFE
    │       ├── S2A_MSIL1C_20180506T002101_N0206_R116_T55HBV_20180506T014715.SAFE
    │       ├── S2A_MSIL1C_20180509T002711_N0206_R016_T55HBV_20180509T033541.SAFE
    │       ├── S2A_MSIL1C_20180516T002101_N0206_R116_T55HBV_20180516T014607.SAFE
    │       ├── S2A_MSIL1C_20180519T002711_N0206_R016_T55HBV_20180519T015836.SAFE
    │       ├── S2A_MSIL1C_20180526T002101_N0206_R116_T55HBV_20180526T014739.SAFE
    │       ├── S2A_MSIL1C_20180529T002711_N0206_R016_T55HBV_20180529T020042.SAFE
    │       ├── S2B_MSIL1C_20180411T002049_N0206_R116_T55HBV_20180411T014716.SAFE
    │       ├── S2B_MSIL1C_20180414T002709_N0206_R016_T55HBV_20180414T015855.SAFE
    │       ├── S2B_MSIL1C_20180424T002709_N0206_R016_T55HBV_20180424T020423.SAFE
    │       ├── S2B_MSIL1C_20180504T002709_N0206_R016_T55HBV_20180504T020239.SAFE
    │       ├── S2B_MSIL1C_20180511T002059_N0206_R116_T55HBV_20180511T015205.SAFE
    │       ├── S2B_MSIL1C_20180514T002709_N0206_R016_T55HBV_20180514T014806.SAFE
    │       ├── S2B_MSIL1C_20180521T002049_N0206_R116_T55HBV_20180521T032735.SAFE
    │       ├── S2B_MSIL1C_20180524T002709_N0206_R016_T55HBV_20180524T014647.SAFE
    │       └── S2B_MSIL1C_20180531T002049_N0206_R116_T55HBV_20180531T013551.SAFE
    └── L2A
        ├── T54HXE
        │   └── S2B_MSIL2A_20180411T002049_N0206_R116_T54HXE_20180411T014716.SAFE
        └── T54HYE
            ├── S2A_MSIL2A_20180516T002101_N0206_R116_T54HYE_20180516T014607.SAFE
            ├── S2A_MSIL2A_20180529T002711_N0206_R016_T54HYE_20180529T020042.SAFE
            ├── S2B_MSIL2A_20180424T002709_N0206_R016_T54HYE_20180424T020423.SAFE
            ├── S2B_MSIL2A_20180511T002059_N0206_R116_T54HYE_20180511T015205.SAFE
            ├── S2B_MSIL2A_20180514T002709_N0206_R016_T54HYE_20180514T014806.SAFE
            ├── S2B_MSIL2A_20180524T002709_N0206_R016_T54HYE_20180524T014647.SAFE
            └── S2B_MSIL2A_20180531T002049_N0206_R116_T54HYE_20180531T013551.SAFE
            
    └── GAP
```

## 6. Limitaions 

At the present, there are following limitations of SITS Processing Chain:

1. It only supports Linux system (testing on Ubuntu 16.04).
2. This code relies on Python 2.7.
3. It is only optimised for Sentinel-2 data format from 2016-12-15 till now. Later on, it will support more data sources.
4. It only supports for downloading data by tiles. Later on, we will support by cities and locations.
5. Ozone value is only available for Victoria Australia.
6. MAJA processor is not available at this moment
7. At this moment, due to time limit, only first two stages are working effectively. The third stage is under developing.
8. History Sentinel-2 Data for Victoria are not fully provided by CNES. Some data storing on TAPE should be requested by formal application.
9. Duplicated data exits. 
10. The latest version of Sen2cor (Atmospheric Correction Tool) is not robust enough when dealing with multi-format Sentinel-2 data.
11. The Installation and configuration of IOTA2 is quite complex and time consuming.