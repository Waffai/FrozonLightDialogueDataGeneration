


# test case for function get_uploaded_files
 def test_get_uploaded_files():
        print("Start test_get_uploaded_files")
        print("Start uploading files...")
        file_path = "test_files/1.mp3"
        file_name = "1.mp3"
        file_size = os.path.getsize(file_path)
        file_type = "audio/mp3"
        asset_dict = upload_file(file_path, file_name, file_size, file_type)
        print("Uploading files completes.")
        print("asset_dict:", asset_dict)
        print("End test_get_uploaded_files")
