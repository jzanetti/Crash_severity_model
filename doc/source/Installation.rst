Installation
=====

This page contains the instructions about how to install **Crash Severity Model**

The package management tool ``conda`` is required for installing **Crash Severity Model**.

CONDA Installation
^^^^^^^^^
**Crash Severity Model** is a package manager which support multiple languages including python. It can be installed as below:

- **step 1**: Download `miniconda` from  `[here] <https://docs.conda.io/en/latest/miniconda.html>`_
- **step 2**: the package can be installed as ``bash Miniconda3-latest-Linux-x86_64.sh``, or following the instruction `[here] <https://conda.io/projects/conda/en/latest/user-guide/install/linux.html>`_

After the installation, **CONDA** environment can be activated using ``conda activate <env>``


Crash Severity Model Installation
^^^^^^^^^
After ``conda``, **Crash Severity Model** can be simply installed with the provided ``makefile`` in the repository:

.. code-block:: bash

   export CONDA_BASE=<CONDA PATH>
   make all

where ``CONDA_BASE`` is the path where the ``conda`` package is installed. For example, we can have ``export CONDA_BASE=~/Programs/miniconda3/``.

The working environment then can be activated as:

.. code-block:: bash

   conda activate crash_severity_model


Input data
^^^^^^^^^
The following dataset are required to be downloaded:

- For model training: ``Crash Analysis System`` (CAS) data is required to be downloaded from the NZTA website

- For prediction:

   - ``NZ Road Centreline`` (*shapefile*): The national road centre line is needed (`[link] <https://data.linz.govt.nz/layer/50329-nz-road-centrelines-topo-150k/>`_)
   - ``NZ Road Slope`` (*tiff*): Road slope dataset (`[link] <https://lris.scinfo.org.nz/layer/107239-nzenvds-slope-degrees-v10/>`_)
   - ``NZ Speed Limit Register`` (*shapefile*): Road speed limit dataset from NZTA (`[link] <https://opendata-nzta.opendata.arcgis.com/maps/aa376f1f2f3643bdac4d18855229239c>`_)

The above data must be placed in ``etc/data`` as:

   .. list-table:: Input data location
      :widths: 25 25
      :header-rows: 1

      * - Data name
      - data location
      * - ``Crash Analysis System``
      - ``etc/cas.csv``
      * - ``NZ Road Centreline``
      - ``etc/road_centreline``
      * - ``NZ Road Slope``
      - ``etc/road_slope``
      * - ``NZ Speed Limit Register``
      - ``road_speedlimit``

The above locations can be adjusted within ``process/__init__.py``.