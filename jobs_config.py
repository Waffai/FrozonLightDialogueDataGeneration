jobs_config = {
  "work_directory": "/programs/automation_gpt_generated_dialogue",
  "data_directory": "/data/automation_gpt_generated_dialogue/",
  "cooling_time": 5,
  "storage_time": 1440,
  "steps": {
    "generate_dialogue": {
      "description": "Communicate with GPT and save gpt output to text file",
      "detailed_steps": [
        "1. Communicate with GPT, Get gpt output",
        "2. Change output to json format and add recordName: UUID key/value to each gpt output record",
        "3. Save: Save gpt output in json ready format to text file in ready_gpt_text"
      ],
      "input": [
        "openai gpt api"
      ],
      "output_directory": "gpt_text",
      "outputs": "Text files containing gpt output"
    },

    "add_audios": {
      "description": "Convert text file to audio file using Azure Text to Speech API",
      "compress_audio": False,
      "detailed_steps": [
        "Cooling Checking: Check cooled files (existed more than cooling time) from ready_gpt_text, if found, save the files name in a file name array: converting_audios",
        "Extract Text: Get text from the saved file array",
        "Convert Questions: Convert question in text to audio file using Azure Text to Speech API",
        "Optional Compression: Compress the audio file to mp3 format",
        "Save: Save audio files to output directory ready_to_upload_audios, the file name is the recordsName from step 1",
        "Move: Move text files within file name array to ready_to_upload"
      ],
      "input": [
        "Output_from_step1",
        "azure text to speech api"
      ],
      "outputs": "Audio files",
      "input_directory": "gpt_text",
      "output_directory": "ready_to_upload"
    },

    "upload_records": {
      "description": "Upload audio files to icloud drive",
      "detailed_steps": [
        "Check Cooling: Check cooled audio files (existed more than double cooling time 2*) from ready_to_upload, if found, save the files name in an array: uploading_audios",
        "Upload: Upload Audio Files: Upload audio files to icloud drive",
        "Move: Move audio files in uploading_audios array from ready_to_upload to last_uploaded"
      ],
      "input": [
        "ready_to_upload"
      ],
      "input_directory": "ready_to_upload",
      "output_directory": "last_uploaded"
    },

    "clean_uploaded": {
      "description": "Clean uploaded audio file and text file existed for 1 day",
      "detailed_steps": [
        "Delete: Delete audio and text files in last_uploaded directory older than 1 day"
      ],
      "input_directory": "last_uploaded"

    }
  }
}
