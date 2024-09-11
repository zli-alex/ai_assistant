import unittest
import json, os, sys
from schedule_chatbot import run_schedule_chatbot

def run_and_compare_helper(input_name, actual_output_name, expected_output_name):
    # run the program
    run_schedule_chatbot(user_input_file=f"../tests/test_inputs/{input_name}", output_filename=f"../tests/test_actual_outputs/{actual_output_name}")
    
    # read json for expected output
    with open(f'../tests/test_expected_outputs/{expected_output_name}', 'rb') as f:
        expected_json = json.load(f)
    
    # run our program for actual output
    with open(f'../tests/test_actual_outputs/{actual_output_name}', 'rb') as f:
        actual_json = json.load(f)
    return [expected_json, actual_json]

class TestFC(unittest.TestCase):
    def test_1(self):
        input_name = "test_input_1.json"
        actual_output_name = "actual_output1.json"
        expected_output_name = "golden_output1.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
    
    def test_2(self):
        input_name = "test_input_2.json"
        actual_output_name = "actual_output2.json"
        expected_output_name = "golden_output2.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_3(self):
        input_name = "test_input_3.json"
        actual_output_name = "actual_output3.json"
        expected_output_name = "golden_output3.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
    
    def test_4(self):
        input_name = "test_input_4.json"
        actual_output_name = "actual_output4.json"
        expected_output_name = "golden_output4.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
    
    def test_5(self):
        input_name = "test_input_5.json"
        actual_output_name = "actual_output5.json"
        expected_output_name = "golden_output5.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_6(self):
        input_name = "test_input_6.json"
        actual_output_name = "actual_output6.json"
        expected_output_name = "golden_output6.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
    
    def test_7(self):
        input_name = "test_input_7.json"
        actual_output_name = "actual_output7.json"
        expected_output_name = "golden_output7.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_8(self):
        input_name = "test_input_8.json"
        actual_output_name = "actual_output8.json"
        expected_output_name = "golden_output8.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
    
    def test_9(self):
        input_name = "test_input_9.json"
        actual_output_name = "actual_output9.json"
        expected_output_name = "golden_output9.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_10(self):
        input_name = "test_input_10.json"
        actual_output_name = "actual_output10.json"
        expected_output_name = "golden_output10.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_11(self):
        input_name = "test_input_11.json"
        actual_output_name = "actual_output11.json"
        expected_output_name = "golden_output11.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_12(self):
        input_name = "test_input_12.json"
        actual_output_name = "actual_output12.json"
        expected_output_name = "golden_output12.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_13(self):
        input_name = "test_input_13.json"
        actual_output_name = "actual_output13.json"
        expected_output_name = "golden_output13.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_14(self):
        input_name = "test_input_14.json"
        actual_output_name = "actual_output14.json"
        expected_output_name = "golden_output14.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_15(self):
        input_name = "test_input_15.json"
        actual_output_name = "actual_output15.json"
        expected_output_name = "golden_output15.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_16(self):
        input_name = "test_input_16.json"
        actual_output_name = "actual_output16.json"
        expected_output_name = "golden_output16.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_17(self):
        input_name = "test_input_17.json"
        actual_output_name = "actual_output17.json"
        expected_output_name = "golden_output17.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_18(self):
        input_name = "test_input_18.json"
        actual_output_name = "actual_output18.json"
        expected_output_name = "golden_output18.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_19(self):
        input_name = "test_input_19.json"
        actual_output_name = "actual_output19.json"
        expected_output_name = "golden_output19.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_20(self):
        input_name = "test_input_20.json"
        actual_output_name = "actual_output20.json"
        expected_output_name = "golden_output20.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)
        
    def test_21(self):
        input_name = "test_input_21.json"
        actual_output_name = "actual_output21.json"
        expected_output_name = "golden_output21.json"
        expected_json, actual_json = run_and_compare_helper(input_name, actual_output_name, expected_output_name)
        self.assertEqual(expected_json, actual_json)

if __name__ == '__main__':
    # Define the path to the folder
    folder_path = os.path.join("..", "tests", "test_actual_outputs")

    # Check if the folder exists
    if not os.path.exists(folder_path):
        # Create the folder if it doesn't exist
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")
    else:
        print(f"Folder '{folder_path}' already exists.")
    unittest.main()