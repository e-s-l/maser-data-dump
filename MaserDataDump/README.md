# ABOUT


## t4 specifics:

### the venv

To set-up the virtual enviornment:
```
python3 -m venv $HOME/esl/DataDump/.venv
source $HOME/esl/DataDump/.venv/bin/activate
python3 -m pip install -r requirements.txt
```
and then ´´´deactivate´´´ to get outta there.


### requirements:

The ParamFactors file contains necessary multipliers to the values (as well as value names), and hence must be included for interpretation of the messages from the Maser.

Values such as IP addresses are stored in config.py

#### packages:

time, pandas, socket, astropy, datetime c.f. the requirements.txt file