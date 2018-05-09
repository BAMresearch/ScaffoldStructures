


## What it does:
You can generate minimal surface structures in any desired dimension and save them as .stl-file.

Currently the following triply periodic minimal surfaces are available:

 - Schwarz P
 - Schwarz D
 - Gyroid
 - F-RD
 - Neovius
 - iWP
 - L-Type
 - G'
 - Tubular G
 - Tubular P
 - P_W_Hybride
 - I2-Y
 - Skeletal 1 
 - Skelatal 2

## How to run?

The software was tested with Python 3.5 under Ubuntu 18.04. 

You can use the following executable for Windows:
https://sjtdelfs.de/nextcloud/index.php/s/ro5Fnwp6CWq6J7e

Or open the folder in Terminal and run it with: `python3 app.py`
Needed packages are:
- numpy
- vtk
- pypubsub
- wx_py

## Explanation of the sliders:
- **Element number in X,Y,Z direction** - changes the number of elementary cells 

- **Size of spacing in X,Y,Z direction/X,Y,Z_spacing** - changes the surface quality of the structure, distorts the structure  if not changed evenly

- **Hole size +/-** - changes the thickness of the wall seen from the surface


## License

This app was originally developed by J.C. Dinis at Centre for Rapid and Sustainable Product Development, Polytechnic Institute of Leiria, Marinha Grande, Portugal.

It is open-source and available under GNU GPLv2.0.

Link to the original paper:
https://doi.org/10.1016/j.protcy.2014.10.176
