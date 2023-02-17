Welcome to Crash Severity Model
#######

**Crash Severity Model** is an open-source AI model to analyze road crashes and fatalities for New Zealand. The model uses a stacked AI model comprising three estimators:

- Densely Connected Neural Network
- Extreme Gradient Boosting
- K-nearest Neighbours Regression


.. image:: total_crashes2.png
   :width: 600

**Crash Severity Model** is developed by the Ministry of Transport of New Zealand.
This system is under development. 
Any issues/suggestions for this system please go to **Sijin ZHANG** at zhans@transport.govt.nz


.. note::

   **Why a machine/deep learning is required to analyze the crash dataset ?** Tradtionally we look at the factors casuing an accident individually. The drawback is that, 
   among many potential crash reasons, we are not able to identify the major contributor for an accident. For example, an crash was recorded in a rainy day and the 
   vehicle was speeding, at the same time the road had 4 lanes in a hilly area, any traditional approach would struggle to rank the reason for such a crash unless it has investigated 
   thousands of similar cases like a human investigator. In contrast, an AI model can be used to act as a human investigator and extract the story among the complicated relationships 
   from all the potential reasons that may lead to a crash.


Methodology Overview
==========
A stack model is applied in **Crash Severity Model**. It is an ensemble machine learning technique 
that combines multiple base models to improve prediction accuracy.
For example, in this case, the base models are an XGBoost model and a densely connected neural network, 
and the meta-model is a stochastic gradient descent (SGD) model.

- The XGBoost model is a gradient boosting algorithm that is used for tasks such as regression and classification. It works by combining multiple weak learners to create a strong predictor. 

- The dense neural network, on the other hand, is a type of artificial neural network that is made up of multiple layers of interconnected nodes.

- The base models are trained on the input data and produce predictions, which are then used as input features for the meta-model. The meta-model, in this case an SGD model, is trained to make the final prediction based on the predictions from the base models. The SGD model is a linear model that is optimized by updating the model parameters with small steps in the direction of the gradient of the loss function with respect to the model parameters. This allows the model to learn from the base models and make predictions based on the combined information from both base models.

In summary, the stack model is a combination of multiple models that work together to improve the overall accuracy of the prediction.


Contents
==========

.. toctree::

   Installation
   hist
   policy