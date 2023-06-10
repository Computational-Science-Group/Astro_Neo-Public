"""
Unit test for larch score
"""
import sys

import os
import unittest,copy
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
# sys.path.append('gui/')
# import larch_score
from AstroNeo import pathObj


class Test_pathObj(unittest.TestCase):


    # def test_generate_label_single(self):
    #     """
    #     Test Labels with one label
    #     """
    #     data = [1]
    #     result_label = ['s02_1', 'e0', 'sigma_1', 'deltaR_1']
    #     result_s02_label = []
    #     result = larch_score.generate_labels(data)
    #     self.assertEqual(result[0], result_label)
    #     self.assertEqual(result[1], ['s02_1'])
    #     self.assertEqual(result[2], ['sigma_1'])
    #     self.assertEqual(result[3], ['deltaR_1'])
    def test_mutate(self):
        """Test the mutation obj value is change after the mutation
        """
        path = pathObj.XspecSpectrum()
        result = copy.copy(path.get_func())
        path.mutate()

        result_new = copy.copy(path.get_func())

        self.assertNotEqual(result,result_new)
        # for i in result.keys():
        #     self.assertNotEqual(result[i],result_new[i])

    def test_mutate_specific_par(self):
        """Test the mutate parameters is change but not the other parameters
        """

        path = pathObj.XspecSpectrum()
        result = copy.copy(path.get_func())

        first_key = list(result.keys())[0]
        second_key = list(result.keys())[1]
        path.mutate_par(first_key)

        result_new = copy.copy(path.get_func())

        self.assertNotEqual(result[first_key],result_new[first_key])
        for i in result.keys():
            if i != first_key:
                self.assertEqual(result[i],result_new[i])

    def test_ParamsDict(self):
        """
        Test the PathDict class
        """
        params = ['a','b','c']
        ParamsDict = pathObj.ParamsDict(params)

        par_range = {
            'a': (0.00,0.03,0.0001),
            'b': (0.00,0.03,10000,'number'),
            'c': (0.00,0.03,0.002),
        }
        ParamsDict.initialize_range(par_range)

        vals = np.arange(0,0.03,0.0001)
        self.assertIn(ParamsDict.get()['a'],vals)
        vals = np.arange(0,0.03,0.002)
        self.assertIn(ParamsDict.get()['c'],vals)
        vals = np.linspace(0,0.03,10000)
        self.assertIn(ParamsDict.get()['b'],vals)
    # def test_Params






