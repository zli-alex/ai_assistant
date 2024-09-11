import json

with open("./tests/production_tests.txt") as test_file:
    i = 0
    for line in test_file:
        line = line.strip()
        i += 1
        print(f"running {i}")
        inputs_info = {
            "input_info" : line
        }
        with open(f"./tests/test_inputs/test_input_{i}.json", 'w', encoding='utf-8') as input_file:
            json.dump(inputs_info, input_file, ensure_ascii=False, indent=4)