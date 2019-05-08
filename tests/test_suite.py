import unittest
import sys
sys.path.append('./tests')
import test_eda


loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(test_eda))


runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
