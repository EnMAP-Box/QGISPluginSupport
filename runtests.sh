#!/bin/bash
QT_QPA_PLATFORM=offscreen
export QT_QPA_PLATFORM
CI=True
export CI

find . -name "*.pyc" -exec rm -f {} \;
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 runfirst.py

mkdir test-reports
mkdir test-reports/today
python3 -m coverage run --rcfile=.coveragec   tests/test_classificationscheme.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_crosshair.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_cursorlocationsvalues.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_example.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_init.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_layerproperties.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_maptools.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_models.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_plotstyling.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_qgisissues.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_resources.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_speclib_core.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_speclib_gui.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_speclib_io.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_testing.py
python3 -m coverage run --rcfile=.coveragec --append  tests/test_utils.py
python3 -m coverage report