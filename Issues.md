
# Encountered Issue

``` NO_DEPRECATED_API=NPY_1_7_API_VERSION -I/private/var/folders/x9/55cdq9mj5msby1f05d6s0r3m0000gp/T/pip-build-env-jp3foaci/overlay/lib/python3.11/site-packages/numpy/core/include -I/Users/aminatshotade/Desktop/projects/movie-recommendation/mvenv/include -I/Applications/anaconda3/include/python3.11 -c surprise/similarities.c -o build/temp.macosx-11.0-arm64-cpython-311/surprise/similarities.o
      In file included from surprise/similarities.c:44:
      /Applications/anaconda3/include/python3.11/Python.h:23:12: fatal error: 'stdlib.h' file not found
      #  include <stdlib.h>
                 ^~~~~~~~~~
      1 error generated.
      error: command '/usr/bin/clang' failed with exit code 1
      [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for scikit-surprise
Failed to build scikit-surprise
ERROR: Failed to build installable wheels for some pyproject.toml based projects (scikit-surprise)```