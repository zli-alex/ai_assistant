import subprocess, json

with open("./tests/production_tests.txt") as test_file:
    i = 0
    for line in test_file:
        i += 1
        print(f"running {i}")
        inputs_info = {
            "input_info" : line,
            "output_filename" : f"./outputs/output{i}.json"
        }
        with open("./inputs/input_info.json", 'w', encoding='utf-8') as input_file:
            json.dump(inputs_info, input_file, ensure_ascii=False, indent=4)
        subprocess.run(["python3", "schedule_chatbot.py"])