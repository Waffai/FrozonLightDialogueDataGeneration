import json
import random
import os
import shutil
import time

from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechSynthesizer

from jobs_config import jobs_config
from config import config


async def randomVoice(language='English'):
    try:
        with open('./speech-voices.json', 'r') as file:
            voices = json.load(file)
        matchingVoices = [key for key in voices.keys() if voices[key].startswith(language)]
        randomVoice = random.choice(matchingVoices)
        print(randomVoice)
        return randomVoice
    except Exception as error:
        print("Error in randomVoice: ", error)


def speechSynthesis(text="Hello World",
                    voice="en-US-JennyNeural",
                    audioFile="YourAudioFile.wav", speechsdk=None):
    try:
        speech_config = speechsdk.SpeechConfig(subscription=config.azure_speech_key, region=config.azure_speech_region)
        audio_config = speechsdk.audio.AudioOutputConfig(filename=audioFile)

        # The language of the voice that speaks.
        speech_config.speech_synthesis_voice_name = voice
        print("voice name:", voice)

        # Create the speech synthesizer.
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("synthesis finished.")
        else:
            print(
                f"{voice}: Speech synthesis canceled, {result.error_details}\nDid you set the speech resource key and region values?")

        synthesizer.close()
        synthesizer = None
    except Exception as ex:
        print("Error in speechSynthesis:", ex)


def get_cooled_dialogue_json(input_dir, cooling_time):
    # get all files in input_dir
    files = os.listdir(input_dir)
    # get current time
    current_time = time.time()
    # get all files that are older than cooling_time
    cooled_files = []
    for file in files:
        file_path = input_dir + file
        file_time = os.path.getmtime(file_path)
        if current_time - file_time > cooling_time:
            cooled_files.append(file_path)
    # make sure all files in cooled_files are json files
    cooled_files = [file for file in cooled_files if file.endswith('.json')]

    return cooled_files
#
# cat sentence_DsTtJO67mT2Hu1J38shz5gZD.json
# {
#     "recordType": "Sentences",
#     "recordName": "sentence_DsTtJO67mT2Hu1J38shz5gZD",
#     "fields": {
#         "speaker": {
#             "value": "staff"
#         },
#         "en": {
#             "value": "Certainly, we have a grilled salmon with a citrus glaze that's been very popular tonight. Would you like to try that?"
#         },
#         "cn": {
#             "value": "\u5f53\u7136\u6709\uff0c\u6211\u4eec\u4eca\u665a\u7684\u7279\u8272\u83dc\u662f\u67da\u5b50\u5473\u7684\u70e4\u4e09\u6587\u9c7c\uff0c\u975e\u5e38\u53d7\u6b22\u8fce\u3002\u60a8\u60f3\u5c1d\u8bd5\u4e00\u4e0b\u5417\uff1f"
#         }
#     }
# # }


# main
if __name__ == '__main__':
    print("Preparation: Input and Output dir.")
    input_dir = os.path.join(os.path.expanduser("~"), jobs_config["data_directory"],
                             jobs_config["steps"]["add_audio"]["input_directory"])

    output_dir = os.path.join(os.path.expanduser("~"), jobs_config["data_directory"],
                              jobs_config["steps"]["add_audio"]["output_directory"])
    cooling_time = jobs_config["cooling_time"]

    # if output_dir not exist, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Step 1: Cooling Checking: Check cooled files (existed more than cooling time) from ready_gpt_text, " +
          "if found, save the files name in a file name array: converting_audios")

    ready_to_convert_dialogue = get_cooled_dialogue_json(input_dir, cooling_time)

    print("Step 2: Convert text to audio: Convert text to audio using Azure Cognitive Services, " +
            "if success, move the file to output_dir." )

    # for dialogue in ready_to_convert_dialogue
    for dialogue in ready_to_convert_dialogue:
        # name start with "sentence", otherwiese skip
        if not dialogue.startswith('sentence'):
            continue

        # read the json file
        with open(dialogue, 'r') as file:
            dialogue_json = json.load(file)

        # get the text
        text = dialogue_json['fields']['en']['value']
        # get the speaker
        speaker = dialogue_json['fields']['speaker']['value']
        # get the dialogue id
        dialogue_id = dialogue_json['recordName']

        # get the voice
        voice = randomVoice(speaker)
        # get the audio file name
        audio_file = dialogue_id + '.wav'
        # get the audio file path
        audio_file_path = os.path.join(output_dir, audio_file)

        # convert text to audio
        speechSynthesis(text, voice, audio_file_path)

        print("Step 3: move the json file to output_dir")
        # move the json file to output_dir
        shutil.move(dialogue, output_dir)








