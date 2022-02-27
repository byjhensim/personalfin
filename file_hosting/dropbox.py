import dropbox


class DropboxUtility:
    def __init__(self, access_token):
        self.access_token = access_token
    
    def upload_file(self,file,file_to):
        """
        Upload files to Dropbox using API v
        """
        dbx = dropbox.Dropbox(self.access_token)
        mode = dropbox.files.WriteMode.overwrite        
        try:
            res= dbx.files_upload(file, file_to, mode=mode)        
        except Exception as err:
            print('***API error', err)
            return None

        return res.name.encode('utf8')