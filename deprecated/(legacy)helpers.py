import openai, re, json
def get_asst_answer(client, prompt, asst_id):
    # Create a thread for the assistant
    thread = client.beta.threads.create()

    # Create message
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    # Run the assistant to get a response
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=asst_id
    )

    # Retrieve the assistant's response
    while run.status in ["queued", "in_progress"]:
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        # print(f"Run status: {keep_retrieving_run.status}")

        if keep_retrieving_run.status == "completed":
            # print("\n")

            # Retrieve the Messages added by the Assistant to the Thread
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )

            return messages.data[0].content[0].text.value

        elif keep_retrieving_run.status == "queued" or keep_retrieving_run.status == "in_progress":
            pass
        else:
            print(f"Run status: {keep_retrieving_run.status}")
            return ""
        
def get_summary(client, prompt, asst_id):
    answer = get_asst_answer(client, prompt, asst_id)
    # print(answer)
    asst_ans_list = answer.strip().split("。")
    # print(asst_ans_list)
    summary = {}
    for sec in asst_ans_list:
        if "：" not in sec:
            continue
        grade, describe = sec.strip().split("：")
        summary[grade] = describe.strip().split("；")
    
    return summary

def get_json(client, prompt, asst_id):
    answer = get_asst_answer(client, prompt, asst_id)
    print(answer)
    answer.replace('\\"', '"')
    start = answer.find("{")
    end = answer.rfind("}")
    data = json.loads(answer[start:end+1])
    if 'constraintJsons' in data.keys():
        data['constraintJsons'] = [json.loads(constraint.replace('\\"', '"')) for constraint in data['constraintJsons']]
    elif 'constraintJson' in data.keys():
        data['constraintJson'] = [json.loads(constraint.replace('\\"', '"')) for constraint in data['constraintJson']]
    else:
        print("Missing constraintJson or constraintJsons")
        return {}
    return data