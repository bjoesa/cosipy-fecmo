#!/usr/bin/env python

'''
    This is the execution code file of the fau-fdm.
    Execute it and your happy.
'''

import logging
import logging.handlers
from datetime import datetime
from os import getpid

from config import debug_level
from core.cosima import cosima


''' Logger setup '''

if (debug_level == 0):
    start_day = '{:%Y-%m-%d}'.format(datetime.now())
    start_time = datetime.now().strftime('%H:%M:%S.%f') #[:-2]
    print ('DEBUG LEVEL = [', debug_level, '] >> No infos, no debugging. This is a pure model run. \n')
    print ('Believe me, it`s pure. \nIt started on', start_day, 'at', start_time, 
           '\nand has got the process number', getpid(), '.')
else:
    
    start_time = datetime.now().strftime('%H:%M:%S.%f')
    # define and open a log file
    log_fh = open("./output/cosipy.log", "w", encoding="utf-8")
    logging.basicConfig(level=debug_level,
                        format='%(asctime)s %(name)-30s %(levelname)-8s %(message)s',
                        datefmt='%d.%b %H:%M')
    
    # %(asctime)s %(module)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s
    
    # define a Handler which writes messages to the sys.stderr
    console = logging.StreamHandler(log_fh)
    console.setLevel(debug_level)
    formatter = logging.Formatter('%(asctime)s %(name)-30s %(levelname)-8s %(message)s')
    #formatter = logging.Formatter('%(asctime)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s')
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    
    log = logging.getLogger('COSIPY')
    log.info('Start: ' + start_time + ' h')
    log.info('Process number: [' + str(getpid()) + ']')
    
    if (debug_level == 10):
        log.debug('DEBUG LEVEL = [' + str(debug_level) + '] >> Fine debugging...')
    elif (debug_level == 20):
        log.debug('DEBUG LEVEL = [' + str(debug_level) + '] >> Coarse debugging...')
    elif (debug_level == 30):
        log.debug('DEBUG LEVEL = [', debug_level, '] >> Show warning, error and crash info...')
    elif (debug_level == 40):
        log.debug('DEBUG LEVEL = [', debug_level, '] >> Show error and crash info...')
    elif (debug_level == 50):
        log.debug('DEBUG LEVEL = [', debug_level, '] >> Show crash info...')
    else:
        log.warning('DEBUG LEVEL = [', debug_level, '] >> Oops! Something´s wrong')
        


''' Main function '''

def main():
    
    logging.info('Start processing...')
    
    cosima()

''' MODEL EXECUTION '''
if __name__ == "__main__":
    
    main()
    
    FMT = '%H:%M:%S.%f'
    stop_time = datetime.now().strftime('%H:%M:%S.%f')
    tdelta = datetime.strptime(stop_time, FMT) - datetime.strptime(start_time, FMT)
    
    if (debug_level == 0):
        print ('It stopped at', stop_time, 'and took', tdelta, 'hours.')
    else:
        log.info('Stoptime: ' + str(stop_time) + ' h')
        log.info('Timedelta: ' + str(tdelta) + ' h')
