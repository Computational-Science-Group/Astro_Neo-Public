#!/bin/bash


# Check for os type
# if [[ "$(uname)" == "Linux" ]]; then
#   echo "This script is running on a Linux system"
# elif [[ "$(uname)" == "Darwin" ]]; then
#   echo "This script is running on a macOS system"
# else
#   echo "This script is running on an unknown operating system"
# fi

# OS_type=$(uname)


# This script is used to import the xspec data into the database

export ATOMDB=$HOME/atomdb
export HEADAS=$HOME/projects/xspec/heasoft-6.31.1/aarch64-apple-darwin22.4.0
source "$HEADAS"/headas-init.sh
