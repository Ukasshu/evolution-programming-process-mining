cd PonyGE2\src

echo ":::Preparing grammar :::"
python prepare.py
 
echo ":::Running algorithm :::"
python ponyge.py

echo ":::Generating diagram:::"
python finish.py


cd ..\..