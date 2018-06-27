# Extraction data from PEPS(French Sentinel mirror site)


## Introduction
PEPS is a mirror site that distributes all the Sentinel data in near real time. Recently, real time was not available for Sentinel-2, as the data format has been deeply changed. PEPS team created a new collection, named "Sentinel-2 Single Tiles", coded "S2ST" to separate the old format form the new one.

"At the same time, as the amount of data on the system nears two petabytes, PEPS started to migrate older data to tapes. The disks work as a cache, all the data are on tape, and only the recently acquired or downloaded data will stay on the frontal disks. The consequence is a longer access time to the data on tape, around one minute. As a compensation, the download rate of PEPS data has been considerably increased."(Olivier, New version of PEPS)


## Authentification 

The file peps.txt must contain your email address and your password on the same line, such as:

`your.email@address.fr top_secret`

To get an account : https://peps.cnes.fr/rocket/#/register


## Sample script
According to Olivier's python script, we have the following ways to download data from PEPS:

- Download all the S2 Single Tiled products acquired above Toulouse in December 2016 of January 2017
`python peps_download.py -l 'Toulouse' -a peps.txt -d 2016-12-06 -f 2017-02-01 -c S2ST`
- Download all the S2 Single Tiled products acquired above Toulouse in December 2016 of January 2017 from relative orbit 51
`python peps_download.py -l 'Toulouse' -a peps.txt -d 2016-12-06 -f 2017-02-01 -c S2ST -o 51`
- Download all the S1 Single Tiled products acquired above Bordeaux in November 2014
`python  peps_download.py -l 'Bordeaux' -a hagolle.txt -d 2014-11-01 -f 2014-11-30 -c S1`
- Download all the S2 multiple tiles products acquired above Toulouse in November 2015
`python peps_download.py --lon 1 --lat 44 -a peps.txt -d 2015-11-01 -f 2015-12-01 -c S2`
- Download all the S2 multiple tiles products acquired above a box near Toulouse in November 2015
`python peps_download.py --lonmin 1 --lonmax 2 --latmin 43 --latmax 44 -a peps.txt -d 2015-11-01 -f 2015-12-01 -c S2`


## Main Process

The original python script is developed by Olivier Hagolle ( https://github.com/olivierhagolle/peps_download ).

We modified it by add tile option and the ability to chose cloudCover. The source code is in https://github.com/cococ0j/peps_download_tile_cloud .

Here, we use "-w" to specify the target fold we store the data. According to new rules of PEPS, products after '2016-12-05' are stored in Tiled products collection, please use option -c S2ST to get the products after that date. So, in order to download data from 2016-06-01 to 2017-06-01, we use two following steps:

1. Step one, download product from 2016-06-01 to 2016-12-04.
`python peps_download.py -l 'Bendigo' -a peps.txt -d 2016-06-01 -f 2016-12-04 -c S2 -w /Users/jibusi/Downloads/winterproject/data/Bendigo1` --ul 95
2. Step two, download product from 2016-12-05 to 2017-06-01.
`python peps_download.py -l 'Bendigo' -a peps.txt -d 2016-12-05 -f 2017-06-01 -c S2ST -w /Users/jibusi/Downloads/winterproject/data/Bendigo2` --ul 95 




