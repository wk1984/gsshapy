'''
********************************************************************************
* Name: All Tests
* Author: Nathan Swain
* Created On: August 7, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
'''
import unittest
from gsshapy.tests.read_tests import TestReadMethods
from gsshapy.tests.write_tests import TestWriteMethods

def all_tests():
    # Retrieve tests
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestReadMethods)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestWriteMethods)
    return unittest.TestSuite([suite1, suite2])

def run_all_tests(verbosity):
    # Retrieve tests
    alltests = all_tests()
    
    # Execute all tests
    unittest.TextTestRunner(verbosity=verbosity).run(alltests) 


if __name__  == '__main__':
    run_all_tests(verbosity=2)