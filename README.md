KoALA-Nx(Korean Accessibility and Optimal Location Analysis Tools - Network)
=============================

KoALA-Nx supports optimal network analysis in various network environments. Users can apply the tool in all network environments, such as roads, railroads, and pedestrians. KoALA-Nx provides two functions: distance-based network analysis and time-based network analysis.
- distance-based network analysis
- time-based network analysis

Prerequisites
------------------------------
- Reference Data(In Korea)
    * Standard Node/Link : [National Transport Information Center(Node, Link)](http://nodelink.its.go.kr/data/data01.aspx)
    * Administrative area : [Korea National Spatial Data Infrastructure Portal(Administrative area)](http://data.nsdi.go.kr/dataset/15144)
    * Road(To create node&link data) : [Korea National Spatial Data Infrastructure Portal(Road)](http://data.nsdi.go.kr/dataset/12902)
- QGIS Minimum Version >= 3.10
- Requires 'pandas' library
     
Installation Process
------------------------------
You must install **'pandas'** to use this plugin. Manual installation is as follows.

- Windows
    * Open the **OSGeo4W shell** that has been installed alongside QGIS (click [Start] - [OSGeo4W Shell])
    * Paste the command **'python-qgis -m pip install pandas'** into the shell
    * Accept the installation by typing **'yes'** when prompted
    * Restart **QGIS3**

- Linux
    * Open a **terminal**
    * Paste the command **'python-qgis -m pip install pandas'** into the terminal
    * Accept the installation by typing **'yes'** when prompted
    * Restart **QGIS3**

- macOS
    * Open a **terminal**
    * Paste the command **'/Library/Frameworks/Python.framework/Versions/3.x/bin/pip3.x install pandas'** into the terminal, (please replace the version number x according to your installation)
    * Accept the installation by typing **'yes'** when prompted
    * Restart **QGIS3**


Plugins Repository
------------------------------
- https://github.com/ansup0402/KoALA_Nx


License
------------------------------
 - [GNU General Public License, version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

