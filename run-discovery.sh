#!/bin/bash

cd PonyGE2/src

echo ":::Preparing grammar :::"
python prepare.py
echo "Done!"
 
echo ":::Running algorithm :::"
python ponyge.py
echo "Done!"

echo ":::Generating diagram:::"
python finish.py
echo "Done!"

cd ../..