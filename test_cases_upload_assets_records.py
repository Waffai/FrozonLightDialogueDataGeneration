def test():
    question = {"recordType": "Questions", "recordName": "4827480773892b44bf6315f3ad879bf1", "fields": {
        "question": {"value": "Please enroll in the computer science program before the deadline."},
        "difficulty": {"value": 2}, "chinese": {"value": "请在截止日期前报名计算机科学专业。"},
        "germany": {"value": "Bitte melden Sie sich vor dem Stichtag für das Informatikkursprogramm an."},
        "japanese": {"value": "締め切り前にコンピュータ科学プログラムに登録してください。"}, "germanyAcademicVocabulary": {
            "value": "[{\"word\":\"Stichtag\",\"phonetic\":\"/ˈʃtɪç.taːk/\",\"definition\":\"a deadline or target date\"},{\"word\":\"Informatikkursprogramm\",\"phonetic\":\"/ɪnˈfɔːr.ma.tɪk ˈkʊrs ˈprəʊ.ɡræm/\",\"definition\":\"computer science course program\"}]"},
        "japaneseAcademicVocabulary": {
            "value": "[{\"word\":\"締め切り\",\"phonetic\":\"/しめきり/\",\"definition\":\"deadline\"},{\"word\":\"コンピュータ科学\",\"phonetic\":\"/こんぴゅーたかがく/\",\"definition\":\"computer science\"},{\"word\":\"登録\",\"phonetic\":\"/とうろく/\",\"definition\":\"registration\"}]"},
        "academicVocabulary": {
            "value": "[{\"word\":\"enroll\",\"phonetic\":\"/ɪnˈrəʊl/\",\"definition\":\"to put yourself or someone else onto the official list of members of a course, college, or group\"},{\"word\":\"computer science\",\"phonetic\":\"/kəmˈpjuː.tər ˈsaɪ.əns/\",\"definition\":\"the academic study of computers and their applications\"},{\"word\":\"deadline\",\"phonetic\":\"/ˈdedˌlaɪn/\",\"definition\":\"a date or time by which something must be done\"}]"}}}
    question_name = question["recordName"]
    question_type = question["recordType"]
    question_fields = question["fields"]
    question_fields["question"]["value"] = "Please enroll in the computer science program before the deadline."
    question_fields["difficulty"]["value"] = 2
    question_fields["chinese"]["value"] = "请在截止日期前报名计算机科学专业。"
    question_fields["germany"]["value"] = "Bitte melden Sie sich vor dem Stichtag für das Informatikkursprogramm an."
    question_fields["japanese"]["value"] = "締め切り前にコンピュータ科学プログラムに登録してください。"
    question_fields["germanyAcademicVocabulary"][
        "value"] = "[{\"word\":\"Stichtag\",\"phonetic\":\"/ˈʃtɪç.taːk/\",\"definition\":\"a deadline or target date\"},{\"word\":\"Informatikkursprogramm\",\"phonetic\":\"/ɪnˈfɔːr.ma.tɪk ˈkʊrs ˈprəʊ.ɡræm/\",\"definition\":\"computer science course program\"}]"
    question_fields["japaneseAcademicVocabulary"][
        "value"] = "[{\"word\":\"締め切り\",\"phonetic\":\"/しめきり/\",\"definition\":\"deadline\"},{\"word\":\"コンピュータ科学\",\"phonetic\":\"/こんぴゅーたかがく/\",\"definition\":\"computer science\"},{\"word\":\"登録\",\"phonetic\":\"/とうろく/\",\"definition\":\"registration\"}]"
    question_fields["academicVocabulary"][
        "value"] = "[{\"word\":\"enroll\",\"phonetic\":\"/ɪnˈrəʊl/\",\"definition\":\"to put yourself or someone else onto the official list of members of a course, college, or group\"},{\"word\":\"computer science\",\"phonetic\":\"/kəmˈpjuː.tər ˈsaɪ.əns/\",\"definition\":\"the academic study of computers and their applications\"},{\"word\":\"deadline\",\"phonetic\":\"/ˈdedˌlaɪn/\",\"definition\":\"a date or time by which something must be done\"}]"
    print("question:", question)
    print("question_name:", question_name)
    print("question_fields:", question_fields)
    print("question_fields['question']['value']:", question_fields["question"]["value"])
    print("question_fields['difficulty']['value']:", question_fields["difficulty"]["value"])
    print("question_fields['chinese']['value']:", question_fields["chinese"]["value"])
    print("question_fields['germany']['value']:", question_fields["germany"]["value"])
    print("question_fields['japanese']['value']:", question_fields["japanese"]["value"])
    asset_dict = {'size': 135244, 'fileChecksum': 'AfG537QLtwBuTwckDPklnldQbG+y', 'fileName': '4827480773892b44bf6315f3ad879bf1.mp3' }

    question_fields = question["fields"]
    body = {
        "operations": [{
            "operationType": "create",
            "record": {
                "recordName": question["recordName"],
                "recordType": question["recordType"],
                "fields": {
                    "question": {"value": question_fields["question"]},
                    "difficulty": {"value": question_fields["difficulty"]},
                    "chinese": {"value": question_fields["chinese"]},
                    "germany": {"value": question_fields["germany"]},
                    "japanese": {"value": question_fields["japanese"]},
                    "germanyAcademicVocabulary": {"value": question_fields["germanyAcademicVocabulary"]},
                    "japaneseAcademicVocabulary": {"value": question_fields["japaneseAcademicVocabulary"]},
                    "academicVocabulary": {"value": question_fields["academicVocabulary"]},
                    "audio": {"value": asset_dict}
                }
            }
        }]
    }
    print("body:", body)


test()


