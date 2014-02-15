#!/bin/bash

dead=0
alive=0

function test {
    mut=`"$@" 2> /dev/null`
    status=$?
    if [ $status -ne 0 ]; then
	dead=$(($dead+1))
    else
	alive=$(($alive+1))
	echo "http://$(hostname):8000/triangle.mut#$mut"
    fi
}

if [ $# -ne 1 ]
then
  echo -e "Usage: `basename $0` {operator}"
  exit
fi

make clean
OPERATOR=$1 make
echo ""
echo "Running $1 mutants..."
./triangle 0 > /dev/null 2>&1 || echo "Test suite contains errors"

count=`./triangle`
for (( i=1; i<=$count; i++ ))
do
    test ./triangle $i
done


echo "==========="
echo "Dead:  $dead"
echo "Alive: $alive"
echo ""
echo "To view mutation reports, start llvm-p86-webserver"
