#!/usr/bin/env python3
"""Stub script for testing Program features."""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import sys ;
import os  ;

import numpy as np

import Utils.TLogProcessor     as tlp ;
import IdtReader.TIdTextReader as irdr
# --------------------------------------------------------------------

def set_error_manager (log_file_s, error_level_i) :
    """
    Set the Log/Error manager
    """
    tlp.get_log_mgr (log_file_s, "w") ;
    tlp.set_log_level (error_level_i) ;

def main():
    """Entry point for the stub script."""
    print("Project Shard - IdtReader environment. Main starting.")
    # Place feature tests here
    print("Project Shard - IdtReader environment. Main done.")


if __name__ == "__main__":
    main()

#--- [EoF] ----------------------------------------------------------

