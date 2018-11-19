#! /bin/bash

set -e # exist immediatly on error

ROOTDIR=$(git rev-parse --show-toplevel || echo $PWD)
cd $ROOTDIR

workdir=$(readlink -f ".test-sandbox")

function cleanup ()
{
  [[ -d ${workdir} ]] && rm -rf ${workdir}
}
trap cleanup EXIT
trap cleanup ERR

set -e

echo "Creating sandbox directory (${workdir}) to work in"
mkdir ${workdir}
cd ${workdir}
echo "Cloning repo into sandbox"
git clone .. pyErrorProp-repo


cat << EOF > test.py
import pyErrorProp

conv = pyErrorProp.UncertaintyConvention()
UQ_ = conv.UncertainQuantity
Q_ = UQ_.Quantity

x = UQ_(10,2,'cm')
y = UQ_(20,2,'cm')

print( x,y,"consistent:",conv.consistent(x,y) )

EOF






echo "Testing pip install"
virtualenv -p python3 env
source env/bin/activate
source ${ROOTDIR}/util-scripts/install_dependencies.sh
cd pyErrorProp-repo
pip install .
cd ..

echo "Looking for installed package in virtualenv"
if ! find ./env -iname 'pyErrorProp'
then
  echo "ERROR: did not find pyErrorProp in virtual environment's site packages directory."
  exit 1
fi

echo "Trying to use installed package"
python test.py


deactivate
rm -r env


echo
echo "Testing 'manual' install"

virtualenv -p python3 env
source env/bin/activate
source ${ROOTDIR}/util-scripts/install_dependencies.sh
cp -r pyErrorProp-repo/pyErrorProp ./
pwd
ls -l
python test.py
