import json
import os
import random
import string
from typing import Dict

import openai
from jobs_config import jobs_config
from config import config
from scenes_keywords import scenes_keywords

# set up the OpenAI API
openai.organization = config['openai_organization']
openai.api_key = config['openai_apiKey']
openai_model = config['openai_model']


def generate_dialogue_dict(scenario, keywords, length=6) -> Dict:
    prompt = (
        f"Please generate a dialogue for the following scenario: {scenario} "
        f"The number of sentences should be no less than {length}. "
        f"Keywords: {keywords} "
        f"Please format the result as a JSON array. "
        f"Example: "
        '{'
        '  "dialogue_info": {'
        f'    "scene": "{scenario}",'
        f'    "keywords": {keywords}'
        '  },'
        '  "dialogue": ['
        '    {'
        '      "speaker": "staff",'
        '      "en": "Welcome to our cafe! What can I get for you today?",'
        '      "cn": "欢迎来到我们的咖啡馆！您今天想要点些什么？"'
        '    },'
        '    {'
        '      "speaker": "user",'
        '      "en": "Hi, can I get a latte please?",'
        '      "cn": "您好，我想要来一杯拿铁。"'
        '    },'
        '    {'
        '      "speaker": "staff",'
        '      "en": "Sure thing. Would you like anything else?",'
        '      "cn": "好的，还需要点别的吗？"'
        '    },'
        '    {'
        '      "speaker": "user",'
        '      "en": "No, that\'s it. How much is it?",'
        '      "cn": "不需要了，这些就可以了。这些东西多少钱？"'
        '    }'
        '  ]'
        '}'
    )

    response = openai.ChatCompletion.create(
        model=openai_model,
        messages=[
            {"role": "assistant", "content": "Please generate a dialogue for the following scenario: "},
            {"role": "user", "content": prompt}
        ],
        n=1,
        stop=None,
        temperature=0.7,

    )

    print("response message:", response)


    message = response["choices"][0]["message"]
    dialogue = json.loads(message["content"])

    return dialogue


# write dict to json file
def write_dict_to_json_file(dict, file_path):
    with open(file_path, 'w') as f:
        json.dump(dict, f, indent=4)


def format_dialogue_from_gpt_json_to_cloudkit_json(dialogue: Dict) -> Dict:
    sentence_records_names = []
    for sentence in dialogue['dialogue']:
        sentence_record = {
            "recordType": "Sentences",
            "recordName": "sentence_" + generate_record_name(),
            "fields": {
                "speaker": {
                    "value": sentence['speaker']
                },
                "en": {
                    "value": sentence['en']
                },
                "cn": {
                    "value": sentence['cn']
                }
            }
        }
        sentence_records_names.append(sentence_record['recordName'])
        write_dict_to_json_file(sentence_record, os.path.join(output_dir, sentence_record['recordName'] + '.json'))

    dialogue_record = {
        "recordType": "Dialogues",
        "recordName": "dialogue_" + generate_record_name(),
        "fields": {
            "dialogue_info": {
                "value": {
                    "scene": dialogue['dialogue_info']['scene'],
                    "keywords": dialogue['dialogue_info']['keywords']
                }
            },
            "dialogue": {
                "value": ",".join(sentence_records_names)
            }
        }

    }
    write_dict_to_json_file(dialogue_record, os.path.join(output_dir, dialogue_record['recordName'] + '.json'))


def generate_record_name():
    record_name = ''.join(random.choices(string.ascii_letters + string.digits, k=24))
    return record_name  # 24 characters


if __name__ == '__main__':
    # Prepare the output dir
    # get home dir in system
    home_dir = os.path.expanduser('~')
    data_dir = jobs_config["data_directory"]

    # get output dir
    output_dir = jobs_config["steps"]["get_gpt_text"]["output_directory"]
    output_dir = os.path.join(home_dir, data_dir, output_dir)

    # if output dir not exist, create it and all parent dirs
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("output dir:", output_dir)

    # step 1. Communicate with GPT, Get gpt output

    # get a random scene from scenes_keywords
    scene = random.choice(list(scenes_keywords.keys()))
    # get some random keywords for the scene
    keywords = random.sample(scenes_keywords[scene], 3)
    # generate a dialogue dict
    dialogue = generate_dialogue_dict(scene, keywords)

    # step 2. Format the output to cloudkit format
    format_dialogue_from_gpt_json_to_cloudkit_json(dialogue)
