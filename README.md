# QGIS Plugin Support (QPS) 
![build status](https://img.shields.io/bitbucket/pipelines/jakimowb/qgispluginsupport.svg)




This is a small library to support the creation of QGIS Plugins. 

OPS is used in other project like:

EnMAP-Box https://bitbucket.org/hu-geomatics/enmap-box

EO Time Series Viewer https://bitbucket.org/jakimowb/eo-time-series-viewer

Virtual Raster Builder https://bitbucket.org/jakimowb/virtual-raster-builder


## Installation ##


1. Copy the qgs folder into your source code, e.g. ``mymodule/qps``, and ensure that the Qt resource files are compiled:

    ```python
    from mymodule.qps.setup import compileQPSResources
    compileQPSResources()
     ```

2. QPS uses the Qt resource system, e.g. to access icons. This requires to convert the ``qps/qpsresources.qrc`` file 
into a corresponding python module ``qps/qpsresources.py``.  


3. Now you can use the QPS python API. Keep in mind that some of its features need to be 
registered to a running Qt Application or the QGIS Application instance. 
This is preferably done in the ```__init__.py``` of 
your application, e.g. by calling:

    ```python
    from mymodule.qps import initAll
    initAll()
    ```


### Example: Spectral Library Widget ###
The following example shows you how to initialize (for testing) a mocked QGIS Application and to open the Spectral Library  Wdiget: 

```python
from mymodule.qps.testing import initQgisApplication
QGIS_APP = initQgisApplication()


from mymodule.qps import initAll 
from mymodule.qps.speclib.spectrallibraries import SpectralLibraryWidget
initAll()

widget = SpectralLibraryWidget()
widget.show()

QGIS_APP.exec_()
```

Note that the first two lines and the last line are not required if QGIS is already started. 


### Example: unit tests

QPS helps to initialize QgsApplications and to test them without starting an entire QGIS Desktop Application.

See `tests/test_example.py`

```python
import os, pathlib, unittest
from qps.testing import TestCase, StartOptions, start_app

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, QFile, QDir
from qgis.core import QgsApplication

qgis_images_resources = pathlib.Path(__file__).parents[1] / 'qgisresources' / 'images_rc.py'

class Example1(unittest.TestCase):

    @unittest.skipIf(not qgis_images_resources.is_file(), 'Resource file does not exist: {}'.format(qgis_images_resources))
    def test_startQgsApplication(self):
        """
        This example shows how to initialize a QgsApplication on TestCase start up
        """
        resource_path = ':/images/icons/qgis_icon.svg'
        self.assertFalse(QFile(resource_path).exists())

        # StartOptions:
        # Minimized = just the QgsApplication
        # EditorWidgets = initializes EditorWidgets to manipulate vector attributes
        # ProcessingFramework = initializes teh QGIS Processing Framework
        # PythonRunner = initializes a PythonRunner, which is required to run expressions on vector layer fields
        # PrintProviders = prints the QGIS data providers
        # All = EditorWidgets | ProcessingFramework | PythonRunner | PrintProviders

        app = start_app(options=StartOptions.Minimized, resources=[qgis_images_resources])
        self.assertIsInstance(app, QgsApplication)
        self.assertTrue(QFile(resource_path).exists())


class ExampleCase(TestCase):
    """
    This example shows how to run unit tests using a QgsApplication
    that has the QGIS resource icons loaded
    """
    @classmethod
    def setUpClass(cls) -> None:
        # this initializes the QgsApplication with resources from images loaded
        resources = []
        if qgis_images_resources.is_file():
            resources.append(qgis_images_resources)
        super().setUpClass(cleanup=True, options=StartOptions.Minimized, resources=resources)

    @unittest.skipIf(not qgis_images_resources.is_file(),
                     'Resource file does not exist: {}'.format(qgis_images_resources))
    def test_show_raster_icon(self):
        """
        This example show the QGIS Icon in a 200x200 px label.
        """
        icon = QIcon(':/images/icons/qgis_icon.svg')
        self.assertIsInstance(icon, QIcon)

        label = QLabel()
        label.setPixmap(icon.pixmap(QSize(200,200)))

        # In case the the environmental variable 'CI' is not set,
        # .showGui([list-of-widgets]) function will show and calls QApplication.exec_()
        # to keep the widget open
        self.showGui(label)



if __name__ == '__main__':

    unittest.main()

```

## Update pyqtgraph

Run the the following command to the qps internal [pyqtgraph](http://pyqtgraph.org) version
```
git read-tree --prefix=qps/externals/pyqtgraph/ -u pyqtgraph-0.11.0rc0:pyqtgraph
```



## License

QPS is released under the GNU Public License (GPL) Version 3 or above.
Developing QPS under this license means that you can (if you want to) inspect
and modify the source code and guarantees that you, our happy user will always
have access to an EnMAP-Box program that is free of cost and can be freely
modified.


