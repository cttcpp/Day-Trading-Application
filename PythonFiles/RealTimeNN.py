from sys import stdout
import pandas as pd
import numpy as np
import time
import scipy.linalg.blas
import scipy
import datetime

def NNOut(inputs, net, P0 = None, Y0 = None):
    """
    Calculates network output for given inputs
    
    Args:
        P0: prev input data
        Y0: prev output data
        
    Returns:
    Y_NN: Neural Network output for input P
    """
    
    outputs   = np.zeros((net['layers'][-1], np.size(inputs) / net['network'][0]))
    data, net = prepare_data(inputs, outputs, net)
    input_weight_matrices, connection_weight_matrices, bias = convert_vector_to_matrices(net)
    
    network_out = get_network_output(
        data['inputs'], 
        net, 
        input_weight_matrices,                                     
        connection_weight_matrices, 
        bias, 
        layer_outputs     = data['layer_outputs'], 
        num_prev_data_pts = data['q0'])[0]

    # Scale normalized output
    network_out_scaled = network_out.copy()
    for y in range(np.shape(network_out)[0]):
        network_out_scaled[y] = network_out[y] * net['normY'][y]
    
    if np.shape(network_out_scaled)[0] == 1:
        network_out_scaled = network_out_scaled[0]
    
    return network_out_scaled
	
def prepare_data(network_inputs, 
                 network_targets, 
                 network, 
                 prev_input_data0  = None, 
                 prev_output_data0 = None):
    """
    Prepare input data for network training and check for errors
    
    Returns: 
        dict containing data for training or calculating output
    """
    
    # Convert inputs and outputs to 2D array, if 1D array is given
    if network_inputs.ndim == 1:
        network_inputs = np.array([network_inputs])
    
    if network_targets.ndim == 1:
        network_targets = np.array([network_targets]) 
        
    # Check if input and output data match structure of network
    if np.shape(network_inputs)[0] != network['network'][0]:
        raise ValueError("Dimension of input data doesn't match # of inputs of network")
    
    if np.shape(network_targets)[0] != network['network'][-1]:
        raise ValueError("Dimension of output data doesn't match # of outputs of network")
    
    if np.shape(network_inputs)[1] != np.shape(network_targets)[1]:
        raise ValueError("Input and output data must have same # of datapoints")
        
    # Check if prev data given, convert input and output to 2D array, if 1D array given
    if (prev_input_data0 is not None) and (prev_output_data0 is not None): 
        if prev_input_data0.ndim == 1:
            prev_input_data0 = np.array([prev_input_data0])
        
        if prev_output_data0.ndim == 1:
            prev_output_data0 = np.array([prev_output_data0])
            
        # Check if input and output data match structure of network
        if np.shape(prev_input_data0)[0] != network['network'][0]:
            raise ValueError("Dimension of prev input data(p0) doesn't match # inputs of network")
        
        if np.shape(prev_output_data0)[0] != network['network'][-1]:
            raise ValueError("Dimension of prev output data(y0) doesn't match # outputs of network")
        
        if np.shape(prev_input_data0)[1] != np.shape(prev_output_data0)[1]:
            raise ValueError("Prev input and output data must have same # of datapoints(q0)")
            
        num_prev_data_pts = np.shape(prev_input_data0)[1] 
        
        # Init layer outputs
        layer_outputs = {} 
        
        for i in range(1, num_prev_data_pts + 1):
            for j in range(1, network['num_layers']):
                # Layer ouputs of hidden layers are unknown -> set to zero
                layer_outputs[i, j] = np.zeros(network['network'][-1]) 
            
            # Set layer ouputs of output layer
            layer_outputs[i, network['num_layers']] = prev_output_data0[:, i - 1] / network['normY'] 
            
        # Add prev inputs and outputs to input/output matrices
        updated_inputs  = np.concatenate([prev_input_data0, network_inputs], axis=1)
        updated_outputs = np.concatenate([prev_output_data0, network_targets], axis=1)
    
    # Keep inputs and outputs as is and set q0 and a to default vals
    else: 
        updated_inputs    = network_inputs.copy()
        updated_outputs   = network_targets.copy()
        num_prev_data_pts = 0
        layer_outputs     = {}
        
    # Normalize
    inputs_normed  = updated_inputs.copy()
    outputs_normed = updated_outputs.copy()
    
    if 'normP' not in network.keys():
        normInp = np.ones(np.shape(updated_inputs)[0])

        for p in range(np.shape(updated_inputs)[0]):
            normInp[p]       = np.max([np.max(np.abs(updated_inputs[p])), 1.0])
            inputs_normed[p] = updated_inputs[p] / normInp[p]

        normOut = np.ones(np.shape(updated_outputs)[0])

        for y in range(np.shape(updated_outputs)[0]):
            normOut[y]        = np.max([np.max(np.abs(updated_outputs[y])), 1.0])
            outputs_normed[y] = updated_outputs[y] / normOut[y] 
            
        network['normP'] = normInp
        network['normY'] = normOut
   
    else:
        for p in range(np.shape(updated_inputs)[0]):
            inputs_normed[p] = updated_inputs[p] / network['normP'][p]
            
        normOut = np.ones(np.shape(network_targets)[0])
        
        for y in range(np.shape(updated_outputs)[0]):
            outputs_normed[y] = updated_outputs[y] / network['normY'][y]
            
    # Create data dict
    data                   = {}
    data['inputs']         = inputs_normed
    data['outputs']        = outputs_normed
    data['layer_outputs']  = layer_outputs
    data['q0']             = num_prev_data_pts    
    
    return data, network
	
def convert_vector_to_matrices(network):
    """
    Converts weight vector w to Input Weight matrices IW, connection weight 
    matrices LW and bias vectors b
    """
    
    delay_layerM_toL            = network['delay_layerM_toL']       
    delay_input_layer1          = network['delay_input_layer1']       
    inputs_connect_layer1       = network['inputs_connect_layer1']        
    layers_fwd_connect_layerM   = network['layers_fwd_connect_layerM']      
    num_layers_network          = network['num_layers']        
    layers                      = network['layers']   
    inputs                      = network['network'][0]    
    weight_vect_temp            = network['weight_vect'].copy() 
    input_weight_matrices       = {}              
    connection_weight_matrices  = {}              
    bias                        = {}              
    
    for m in range(1, num_layers_network + 1):
        # Input weights
        if m == 1:
            for i in inputs_connect_layer1[m]:
                for d in delay_input_layer1[m, i]:
                    weight_i                       = inputs * layers[m - 1]
                    vec                            = weight_vect_temp[0 : weight_i]
                    weight_vect_temp               = weight_vect_temp[weight_i :]
                    
                    input_weight_matrices[m, i, d] = np.reshape(vec, (layers[m - 1], 
                                                                      len(vec) / layers[m - 1]), 
                                                                      order = 'F')
        
        # Internal connect weights
        for l in layers_fwd_connect_layerM[m]:
            for d in delay_layerM_toL[m, l]:
                weight_i                            = layers[l - 1] * layers[m - 1]
                vec                                 = weight_vect_temp[0 : weight_i]
                weight_vect_temp                    = weight_vect_temp[weight_i :]
                
                connection_weight_matrices[m, l, d] = np.reshape(vec, (layers[m - 1], 
                                                                       len(vec) / layers[m - 1]), 
                                                                       order = 'F')
        
        # Bias vector of layer m
        weight_i         = layers[m - 1]
        bias[m]          = weight_vect_temp[0 : weight_i]
        weight_vect_temp = weight_vect_temp[weight_i :]

    return input_weight_matrices, connection_weight_matrices, bias
	
def get_network_output(network_inputs, 
                       network, 
                       input_weight_matrices, 
                       connection_weight_matrices, 
                       bias, 
                       layer_outputs = {}, 
                       num_prev_data_pts = 0):
    """
    Calculates network output for given inputs
    """
    
    delay_layerM_toL              = network['delay_layerM_toL']                                 
    delay_input_layer1            = network['delay_input_layer1']                                 
    inputs_connect_layer1         = network['inputs_connect_layer1']                                  
    layers_fwd_connect_layerM     = network['layers_fwd_connect_layerM']                                
    num_layers_network            = network['num_layers']                                  
    outputs                       = network['network'][-1]                             
    sum_output_layers             = {}                                        
    num_of_input_datapts          = network_inputs.shape[1]                        
    network_output                = np.zeros((outputs, num_of_input_datapts)) 
    
    # For all datapoints
    for q in range(num_prev_data_pts + 1, num_of_input_datapts + 1): 
        layer_outputs[q, 1] = 0
        # For all layers
        for m in range(1, num_layers_network + 1): 
            # Sum output datapoint q, layer m
            sum_output_layers[q, m] = 0         
            
            # Input weights
            if m == 1:
                for i in inputs_connect_layer1[m]:
                    for d in delay_input_layer1[m, i]:
                        if (q - d) > 0:
                            sum_output_layers[q, m] += np.dot(input_weight_matrices[m, i, d], 
                                                              network_inputs[:, q - d - 1])
                            
            # Connect weights
            for l in layers_fwd_connect_layerM[m]:
                for d in delay_layerM_toL[m, l]:
                    if (q - d) > 0:
                        sum_output_layers[q, m] += np.dot(connection_weight_matrices[m, l, d], 
                                                          layer_outputs[q - d, l])
            # Bias
            sum_output_layers[q, m] += bias[m]
            
            # Calc layer output
            if m == num_layers_network:
                # Linear layer for output
                layer_outputs[q, num_layers_network] = sum_output_layers[q, num_layers_network] 
            else:
                layer_outputs[q, m] = np.tanh(sum_output_layers[q, m])
        
        network_output[:, q - 1] = layer_outputs[q, num_layers_network]
    
    network_output = network_output[:, num_prev_data_pts :]
    
    return network_output, sum_output_layers, layer_outputs