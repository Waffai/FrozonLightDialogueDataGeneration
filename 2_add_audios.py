import asyncio
import json
import random
import os
import shutil
import string
import time

import azure.cognitiveservices.speech as speechsdk

from jobs_config import jobs_config
from config import config

print("Preparation: Input and Output dir.")
input_dir = os.path.join(os.path.expanduser("~"), jobs_config["data_directory"],
                         jobs_config["steps"]["add_audio"]["input_directory"]) + "/"

output_dir = os.path.join(os.path.expanduser("~"), jobs_config["data_directory"],
                          jobs_config["steps"]["add_audio"]["output_directory"]) + "/"
cooling_time = jobs_config["cooling_time"]

# if output_dir not exist, create it
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

#
# speech-voices.json
# "de-DE-ConradNeural": "German, Germany, Male",
# "de-DE-ElkeNeural": "German, Germany, Female",
# "de-DE-GiselaNeural": "German, Germany, Female, Child",
# "de-DE-KasperNeural": "German, Germany, Male",
# "de-DE-KatjaNeural": "German, Germany, Female",
# "en-AU-NatashaNeural": "English, Australia, Female",
# "en-AU-WilliamNeural": "English, Australia, Male",
# "en-CA-ClaraNeural": "English, Canada, Female",
# "en-CA-LiamNeural": "English, Canada, Male",
# "en-GB-AbbiNeural": "English, United Kingdom, Female",
# "en-GB-AlfieNeural": "English, United Kingdom, Male",
# "en-GB-BellaNeural": "English, United Kingdom, Female",
# "en-GB-ElliotNeural": "English, United Kingdom, Male",
# "en-GB-EthanNeural": "English, United Kingdom, Male",
# "en-GB-HollieNeural": "English, United Kingdom, Female",
async def randomVoice(language='English'):
    try:
        with open('./speech-voices.json', 'r') as file:
            voices = dict(json.load(file))
        # based on language, select random voice in keys if language is contained in value
        voices_by_language = [voice for voice in voices.keys() if language in voices[voice]]
        random_voice = random.choice(voices_by_language)
        return random_voice
    except Exception as e:
        print(e)




def speechSynthesis(text="Hello World",
                    voice="en-US-JennyNeural",
                    audioFile="YourAudioFile.wav"):
    try:
        # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
        speech_config = speechsdk.SpeechConfig(subscription=config['azure_speech_key'],
                                               region=config['azure_speech_region'])
        audio_config = speechsdk.audio.AudioOutputConfig(filename=audioFile)

        speech_config.speech_synthesis_voice_name = voice

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")







    #
    #
    #     # Create the speech synthesizer.
    #     synthesizer =SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    #
    #     result = synthesizer.speak_text_async(text).get()
    #
    #     if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    #         print("synthesis finished.")
    #     else:
    #         print(
    #             f"{voice}: Speech synthesis canceled, {result.error_details}\nDid you set the speech resource key and region values?")
    #
    #     synthesizer.close()
    #     synthesizer = None
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
            cooled_files.append(file)
    # make sure all files in cooled_files are json files
    cooled_files = [file for file in cooled_files if file.endswith('.json')]

    return cooled_files

# main
async def main():


    print("Step 1: Cooling Checking: Check cooled files (existed more than cooling time) from ready_gpt_text, " +
          "if found, save the files name in a file name array: converting_audios")

    ready_to_convert_dialogue = get_cooled_dialogue_json(input_dir, cooling_time)

    print("ready_to_convert_dialogue: ", ready_to_convert_dialogue)
    print("Step 2: Convert text to audio: Convert text to audio using Azure Cognitive Services, " +
            "if success, move the file to output_dir." )

    # get the voice await
    voiceBySpeaker = {}

    # for dialogue in ready_to_convert_dialogue
    for cooled_file in ready_to_convert_dialogue:
        # name start with "sentence", otherwiese skip

        file_path = os.path.join(input_dir, cooled_file)
        # read the json file
        with open(file_path, 'r') as file:
            sentence_json = json.load(file)

        # if sentence_json record type not equal to "sentences", skip
        if sentence_json['recordType'] != 'Sentences':
            continue

        # get the text
        text = sentence_json['fields']['en']['value']

        # get the speaker
        speaker = sentence_json['fields']['speaker']['value']
        if voiceBySpeaker.get(speaker) is None:
            voiceBySpeaker[speaker] = await randomVoice()
        # get the dialogue id
        dialogue_id = sentence_json['recordName']


        # time.sleep(1)
        # get the audio file name
        audio_file = dialogue_id + '.wav'
        # get the audio file path
        audio_file_path = os.path.join(output_dir, audio_file)

        # convert text to audio
        speechSynthesis(text, voiceBySpeaker[speaker], audio_file_path)

        print("Step 3: move the json file to output_dir")

        # # move cooled file from input_dir to output_dir
        for cooled_file in ready_to_convert_dialogue:
            file_path = os.path.join(input_dir, cooled_file)
            shutil.move(file_path, output_dir)

asyncio.run(main())



