from bacalhauconnector.data.config import SameConfig
from bacalhauconnector.data.step import Step
from typing import Mapping, Tuple
from pathlib import Path
import os
from pipreqs import pipreqs
#import filecmp
import subprocess
import sys


def render(path: str, steps: Mapping[str, Step], config: SameConfig) -> Tuple[Path, str]:
    inputs = "inputs"
    inputspath = os.path.join(path,inputs)
    os.mkdir(inputspath)
    codefile = os.path.join(inputspath,"code.py")

    # Extract the code from the notebook and write to code.py
    codewriter = open(codefile, "w")
    for name, step in steps.items():
        codewriter.writelines(step.code)
    codewriter.close()


    req=os.path.join(inputspath,"requirements.txt")
    #reqold=os.path.join(inputspath,"requirements.old")
    #if os.path.isfile(req):
    #    os.rename(req,reqold)
    
    # Create a requirements.txt file
    pipreqs.init({'<path>': inputspath, '--savepath': None, '--print': False,
                      '--use-local': None, '--force': True, '--proxy':None, '--pypi-server':None,
                      '--diff': None, '--clean': None, '--mode': 'gt'})
    
    wheelsdir=os.path.join(path,"wheels")
    #if os.path.exists(wheelsdir) and os.path.isfile(reqold) and filecmp.cmp(req,reqold,shallow=True):
    #    pass
    #else:
    subprocess.check_call([sys.executable, "-m", "pip", "download", "-r", req, "-d",wheelsdir,"--prefer-binary"])


    return (path, inputs)
