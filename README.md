# WimpLimitsPlotting

This repository is used to generate plots of WIMP sensitivity curves with experimental results and projections. It is specifically designed for the sensitivity prospects plots of the TREX-DM experiment, focusing on the low-mass range.

The code is based on:
- [DarkMatterLimits](https://github.com/dtemps123/DarkMatterLimits.git)
- [axion-limits](https://github.com/iaxo/axion-limits)

## Code Overview



### WimpPlotClass.py

This file contains the main class `WimpPlot` which is used to create the plots. It takes parameters for x and y limits, a database of DataClass objects, and options to show the excluded region, show the plot, and save the plot. It uses matplotlib to create the plot, with options to set the plot scales, limits, labels, and tick marks. It also includes methods to calculate the excluded parameter space (`getExcludedRegion`), add curves to the plot (`addCurves`), show the plot on screen (`showPlot`), and save the plot to a file (`savePlot`).

This class is kind of a merge between the BasePlot class of https://github.com/iaxo/axion-limits/blob/main/XPlotter.py and WimpPlot class of https://github.com/iaxo/axion-limits/blob/main/wimpPlot.py

### DataClasses.py

This file contains the classes used to represent and manipulate the data used in the plots.

- `DataClass`: This is the base class for all data. It reads data from a file, and stores it along with various metadata such as the source, year, and style of the data. It also provides methods to set parameters from the file header or from options passed to the constructor.

- `Curve`: This class represents a curve on the plot. It extends `DataClass` and adds an interpolator for the data, as well as a method to plot the curve.

- `Contour`: This class represents a contour on the plot. It extends `DataClass` and adds a method to plot the contour.

- `NeutrinoFog`: This class represents a neutrino fog on the plot. It extends `DataClass` and adds a method to plot the fog.

Each class must provide a `plot` method. This method is used by `WimpPlot.addCurves()` to draw that data inside the WimpPlot. Each derive class must provide this method to encode the particularities needed for plotting each kind of data. For example, `Curve` is a line that can be drawn solid (for results) or dashed (for projections), `Contour` must fill the area enclosed by itself and NeutrinoFog must fill the area below its curve.

This classes are inspired by https://github.com/dtemps123/DarkMatterLimits/blob/main/ResultClass.py

### buildDataBase.py

This file contains the function `buildDataBase` which is used to construct the database of DataClass objects used in the plots.

The `buildDataBase` function reads data from a set of files, creates a DataClass object for each file, and adds it to the database. The database is a dictionary where the keys are the names of the data sets and the values are the corresponding DataClass objects.

The function takes no parameters and returns the database. It uses a predefined list of file names and types to read the data. The file names and types are hard-coded in the function. **This file is meant to be modified when updating the experiment results, when you want to change the experiments to be shown (or their color, labels, etc.).**

### generatePlot.py

This file contains the main script to generate the WIMP sensitivity plots. It uses the `WimpPlot` class from `WimpPlot.py` and the `buildDataBase` function from `buildDataBase.py`. If database parameter of WimpPlot is not given, it will call automatically the `buildDataBase` from `builDataBase.py`.
This code is importing the WimpPlot class from the WimpPlotClass module and then creating an instance of the WimpPlot class with default parameters.

The WimpPlot class is used to generate a plot of WIMP sensitivity curves. The class constructor takes several optional parameters to customize the plot, such as the x and y limits, a database of DataClass objects, and options to show the excluded region, show the plot, and save the plot.

In this case, the WimpPlot constructor is called with no parameters, so it will use the default values for all parameters. This will create a plot with the default x and y limits, the default database, and the default options for showing the excluded region and the plot.

The line #WimpPlot(save_plotname = 'prueba1.png') is commented out, but if it were uncommented, it would create a WimpPlot instance and save the plot to a file named 'prueba1.png'.

## Usage

To use this code, simply execute the file generatePlot.py

```bash
python generatePlot.py
```
