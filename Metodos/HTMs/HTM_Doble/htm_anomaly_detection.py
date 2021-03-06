# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 09:33:14 2019

@author: Ming Jin
"""

import json
from nupic.engine import Network
from nupic.encoders import MultiEncoder, ScalarEncoder, DateEncoder


class HTM:
    '''
    The HTM class which packaging the methods that used to create 
    networks and do prediction.
    
    -- getEncoderParams: read encoder parameters from json files
    -- setEncoderParams: write encoder parameters to json files
    -- createNetwork: create HTM network based on parameters and data source
    -- run: run a pre-defined HTM network once if network.run(1). You need to 
            loop this method for iterative prediction on records 
            (see my ipynb file for the usage)
    -- save_network: save the network structure and states after running
    '''
    
    def __init__(self, use_saved_model):
        self.use_saved_model = use_saved_model
    
    
    def getEncoderParams(self, encoder_path, key):
        with open(encoder_path, 'r') as json_file:
            all_params = json.load(json_file)
            return all_params[key]
        
        
    def setEncoderParams(self, encoder_path, encoder_dict):
        with open(encoder_path, 'w') as json_file:
            json.dump(encoder_dict, json_file)
            
            
    def createNetwork(self,
                      datasource,
                      recordParams, 
                      spatialParams, 
                      temporalParams, 
                      verbosity = 0, 
                      model_path = None):
        
        FormacionNIRHumedadPVArgs = recordParams["FormacionNIRHumedadPV"]
        FibraticPredNIRHumedadPVArgs = recordParams["FibraticPredNIRHumedadPV"]

        
        fechaArgs = recordParams["fecha"]
    
        FormacionNIRHumedadPV = ScalarEncoder(**FormacionNIRHumedadPVArgs)
        FibraticPredNIRHumedadPV = ScalarEncoder(**FibraticPredNIRHumedadPVArgs) 



        fecha = DateEncoder(**fechaArgs)
    
        encoder = MultiEncoder()
        encoder.addEncoder(FormacionNIRHumedadPVArgs["name"], FormacionNIRHumedadPV)
        encoder.addEncoder(FibraticPredNIRHumedadPVArgs["name"], FibraticPredNIRHumedadPV)




        encoder.addEncoder(fechaArgs["name"], fecha)
    
        network = Network()
        
        if self.use_saved_model == False:
            network.addRegion("sensor", "py.RecordSensor",
                            json.dumps({"verbosity": verbosity}))
        
            sensor = network.regions["sensor"].getSelf()
            sensor.encoder = encoder
            sensor.dataSource = datasource
        
            # Create the spatial pooler region
            spatialParams["inputWidth"] = sensor.encoder.getWidth()
            network.addRegion("spatialPoolerRegion", "py.SPRegion",
                              json.dumps(spatialParams))
        
            # Link the SP region to the sensor input
            network.link("sensor", "spatialPoolerRegion", "UniformLink", "")
            network.link("sensor", "spatialPoolerRegion", "UniformLink", "",
                         srcOutput="resetOut", destInput="resetIn")
            network.link("spatialPoolerRegion", "sensor", "UniformLink", "",
                         srcOutput="spatialTopDownOut", destInput="spatialTopDownIn")
            network.link("spatialPoolerRegion", "sensor", "UniformLink", "",
                         srcOutput="temporalTopDownOut", destInput="temporalTopDownIn")
        
            # Add the TPRegion on top of the SPRegion
            network.addRegion("temporalPoolerRegion", "py.TMRegion",
                              json.dumps(temporalParams))
        
            network.link("spatialPoolerRegion", "temporalPoolerRegion", "UniformLink", "")
            network.link("temporalPoolerRegion", "spatialPoolerRegion", "UniformLink", "",
                         srcOutput="topDownOut", destInput="topDownIn")
            
            # Add the AnomalyLikelihoodRegion on top of the TMRegion
            network.addRegion("anomalyLikelihoodRegion", "py.AnomalyLikelihoodRegion", json.dumps({}))
            network.link("temporalPoolerRegion", "anomalyLikelihoodRegion", "UniformLink",
                         "", srcOutput="anomalyScore", destInput="rawAnomalyScore")
            network.link("sensor", "anomalyLikelihoodRegion", "UniformLink", "",
                         srcOutput="sourceOut", destInput="metricValue")    
        
        
            spatialPoolerRegion = network.regions["spatialPoolerRegion"]
        
            # Make sure learning is enabled
            spatialPoolerRegion.setParameter("learningMode", True)
            # We want temporal anomalies so disable anomalyMode in the SP. This mode is
            # used for computing anomalies in a non-temporal model.
            spatialPoolerRegion.setParameter("anomalyMode", False)
        
            temporalPoolerRegion = network.regions["temporalPoolerRegion"]
        
            # Enable topDownMode to get the predicted columns output
            temporalPoolerRegion.setParameter("topDownMode", True)
            # Make sure learning is enabled (this is the default)
            temporalPoolerRegion.setParameter("learningMode", True)
            # Enable inference mode so we get predictions
            temporalPoolerRegion.setParameter("inferenceMode", True)
            # Enable anomalyMode to compute the anomaly score.
            temporalPoolerRegion.setParameter("anomalyMode", True)
        
        else:
            network = Network(model_path)
           
        return network
    
    
    def run(self, network):
        sensorRegion = network.regions["sensor"]
        anomalyLikelihoodRegion = network.regions["anomalyLikelihoodRegion"]
        network.run(1)
        anomalyLikelihood = anomalyLikelihoodRegion.getOutputData("anomalyLikelihood")[0]
        fed_in_data = sensorRegion.getOutputData("sourceOut")[0]
        return fed_in_data, anomalyLikelihood
    
    
    def save_network(self, network, model_path):
        network.save(model_path)