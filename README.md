# Instruction of SITS Processing Chain

## 1. Introduction
    This processing chain achieve the serial processes from satellite data downloading, atomospheric correction and gap filling. It composes all three processes into one single command.
    At the present, there are some limitations of SITS Processing Chain. They are as follows:
1. It only supports linux and macOS system.
2. This code relies on python 2.7 so far.
2. It is only optimised for Sentinel-2 data format from 2016-12-15 till now. Later on, it will support more data sources.
2. It only supports for downloading data by tiles. Later on, we will support by cities and locations.
3. Ozone value is only available for Victoria Australia.
4. MAJA processor is not available at this moment



## 2. Prerequisite
### 2.1 Install Sen2Cor
Please see Sen2Cor Configuration and User Manual </a herf='https://step.esa.int/thirdparties/sen2cor/2.4.0/Sen2Cor_240_Documenation_PDF/S2-PDGS-MPC-L2A-SUM-V2.4.0.pdf'>.

One important thing is you should add L2A_Process command into your searching path of your OS.
### 2.2 Install MAJA
### 2.3 Install OTB
### 2.4 Python Libraries
It requires several python libraries, they are as follows:
* pandas, numpy
* lxml
* matplotlib

Make sure you have intall all of them before running this script.



## 2. Modules
### 2.1 sitsProcessChain.py
     It may be the only pyhon script you would like to execute. It reorganize and consolidate all three steps of the satellite data processing. Details are as follows:   
| Parameters |option| description | 
| ------------ | ---------- | ------- |  
| list of tiles | -t| mandatory |
| start date|-d| mandatory (at this time, it should be after 2016-12-15, otherwise we should add more parameter because of peps)|
|end date|-f| mandatory|
|write dir |-w|main absolute path to store data, mandatory|
|l1c dir |-c| directory to store l1c data, will be under main path, default L1C with timestamp|
|l2a dir |-a| directory to store l2a data, will be under main path, default L2A with timestamp|
|gap dir |-g| directory to store gap-filling data, will be under main path, default GAP with timestamp|
|save l1c |--s1| bolean value to choose save l1c data or not after processing, default TRUE|
|save l2a |--s2| boolean value to choose save l2c data or not after processing, default TRUE|
|l2a processor |-lp| either sen2cor or maja, default sen2cor|
| cloud covering lower boundary|--ll| |
|cloud covering upper boundary|--ul| |

### 2.2 pepsDownload.py
Original from [Oliveri's github]( 'https://github.com/olivierhagolle/peps_download). Here, we made some modification so that it can receive cloud covering options from user, and not waste time for downloading data on TAPE, because it is currently unavailable from CENS source. 
### 2.3 configSen2cor.py
This python script is to configure Sen2Cor. You can open and edit it to set parameters. Remeber to save it before you leave.
### 2.4 sen2corProcess.py
This python script is the main file for sen2cor processing. It includes a lookup table for setting Ozone for each satellite file.
## 3. Auxiliary files
| File name | Use |
| -- | -- |
|L2A_GIPP.xml|A copy of default Sen2cor configuration |
| OzoneLUT.csv | Ozone history data for Victoria |
| peps.txt | Peps username and password |

## 4. Workflow
1. Modify configSen2cor.py to set parameters for Sen2Cor
2. Run sitsProcessChain.py with requied parameters


## 5. Examples
### For Sentinel-2
```python 
# Porcess two tiles (54HYE,54HBV) with default saving path
python sitsProcessChain.py -t [54HYE,54HBV] -d 2018-04-14 -f 2018-04-26 -w /Users/jibusi/Downloads/winterproject/data/Test

# Porcess two tiles (54HYE,54HBV) with user-defined saving path and L2A processors
python sitsProcessChain.py -t [54HYE,54HBV] -d 2018-04-14 -f 2018-04-26 -w /Users/jibusi/Downloads/winterproject/data/Test -c l1c_test -a l2a_test -g gap_test --lp sen2cor
```



