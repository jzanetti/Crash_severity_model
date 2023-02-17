

Both the model training and prediction are controlled by configuration files. Some example configuration files are given in ``etc/cfg``





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
    convert: null
    invalid_value: null
  crashSHDescription:
    convert:
      No: 0.0
      Yes: 1.0
    invalid_value: "Unknown"
```

The above section defines two predictos to be used in the model: (1) ``NumberOfLanes`` does not require any value conversion (e.g., to convert a character to a number) 
and there is no invalid value in the dataset. (2) In contrast, for ``crashSHDescription``, we want to convert ``No`` to ``0.0``, and ``Yes`` to ``1.0``, also,
the invalid value for this predictor is ``Unknown``.

This section must be csutomized for different experiments.


Prediction
=====

