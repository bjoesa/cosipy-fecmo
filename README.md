# fau-fdm: Friedrich-Alexander-University Firn Densification Model
    
Author: @bjoesa
    
License: Reuse only with reference to the creators.

The dry_densification scheme is based on Herron and Langway (1980)[1],
you find the PDF e.g. on [cambridge.org](https://www.cambridge.org/core/journals/journal-of-glaciology/article/firn-densification-an-empirical-model/C9A2B038004A938670B689A6DAE6D89E).

## VERY IMPORTANT
The fdm is written in python 3 and tested with Anaconda3 on the Python 3.6.3 Shell.

## Logging control

> Set debug_level in config.py.

Which level should be saved to logfile?

| Level	    | Numeric value | Behaviour							                        |
| ---	    | ---           | ---								                        |
| CRITICAL	| **50**        | Crash info							                    |
| ERROR 	| **40 **       | Still running but erroneus results				        |
| WARNING	| **30**        | Potentially harmful processing				            |
| INFO	    | **20**        | Coarse-grained info (excluding variables)			        |
| DEBUG	    | **10**        | Fine-grained info (including variables and levels 10-50) 	|
| NOTSET	| **0**         | No logging							                    |
     
## Structure

### /

- cosipy: *Main file, execute me!*

    - *Contains main function, logging and debug initialization*


- config: *Make your changes/adaptions here!*

- constants: *Contains variable you usually not change*

### core/

- cosima: *Model framework*

- init_layers: *Module to generate initial layering*

    - init_layers: *inititalize layer properties: layer heights, density, temperature at surface, temperature gradient, liquid water content*


- var_init: *Module to initialize (varInit) and to append to 2D time series arrays*

    - varInit: *initialize arrays*
    - varStore: *append vars to arrays*


- grid: *Contains the code to setup and manipulate the vertical node structure*

- node: *Contains the code to access and manipulate individual nodes*

- inout: *i/o script*

### modules/

- dry_densification: *Physical heart of the model*

- visualization: *Plot functions*

- albedo: 




[1]: Herron, M., & Langway, C. (1980). Firn Densification: An Empirical Model. Journal of Glaciology, 25(93), 373-385. doi:10.3189/S0022143000015239

Hints:

The markdown for this REAME is taken from https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet.
