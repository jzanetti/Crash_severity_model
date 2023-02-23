Policy analysis
=====

The policy analysis model is trained and predicted using a configuration files. Some example configuration files are given in ``etc/cfg``.

Training
=====
The model can be trained using the following three methods:

- ``XGBoost``
- ``SGD``
- A stacked model including both ``XGBoost`` and ``SGD``

The model must be specified in the configuration file. For example,

```
model_name: test
model_type: stack
```

In ``model_type`` you must specify the model name to be exported (in this case it is ``test``), and the model type which you can choose from:

- ``xgb``: XGBoost
- ``knb``: K-neighborhood Regression 
- ``sgd``: Stochastic Gradient Descent model
- ``stack``: An ensemble model contains all the estimators

The target must be specified via the ``target`` section, for example:

```
target:
  name: crashSeverity
  score:
    Non-Injury Crash: 0.0
    Minor Crash: 1.0
    Serious Crash: 2.0
    Fatal Crash: 3.0
```
Here the target variable name is ``crashSeverity``, also different categories of ``crashSeverity`` has different scores, which is used for prediction at a later stage.
In this case, ``Non-Injury Crash`` has no score while ``Fatal Crash`` has the highest score.

We also need to define ``predictors`` in the configuration, e.g.

```
predictors:
  NumberOfLanes:
  crashSHDescription:
  ...
```

The above section defines two predictos to be used in the model. For example, in this section, we have two predictors ``NumberOfLanes`` and ``crashSHDescription``, 
while more predictors can be included.

The model training can be run as:

.. code-block:: bash

  cli_train --workdir <WORKING DIRECTORY>
            --cfg <CONFIGURATION FILE>

where ``--workdir`` indicates the directory where holds all the intermediate and output files, and ``--cfg`` is the configuration file to use.


Prediction
=====

The prediction step is also controlled via a configuration file.

First, we need to define the trained model to be used:

```
model_path: rfm/trained_model_xgb3_no_state_highway.model
```

The model is trained by the previous step.

Second, there are three input data needed for the road policy analysis configuration:

  - Road speed limitation
  - Road centrelines
  - Road slope

The above data can be defined via:

```
inputs:
  nslr: "etc/data/road_speedlimit/National_Speed_Limit_Register_(NSLR).shp"
  road_centrelines: "etc/data/road_centreline/nz-road-centrelines-topo-150k.shp"
  road_slope: "etc/data/road_slope/nzenvds-slope-degrees-v10.tif"
```


