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


class Test_ParamsDict(unittest.TestCase):

    def test_ParamsDict(self):
        """
        Test the ParamsDict class during initialization
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





