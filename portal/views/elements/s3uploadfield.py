from flask_admin import form
from wtforms import ValidationError
import utils
import uuid


class s3UploadField(form.FileUploadField):
    def pre_validate(self, form):
        if self._is_uploaded_file(self.data) and not self.is_file_allowed(
            self.data.filename
        ):
            raise ValidationError("Invalid file extension")

    def _delete_file(self, filename):
        return filename

    def populate_obj(self, obj, name):
        if self._is_uploaded_file(self.data):
            filename = self.generate_name(obj, self.data)
            filename = self._save_file(self.data, filename)
            # update filename of FileStorage to our validated name
            self.data.filename = filename
            setattr(obj, name, filename)
            setattr(obj, "file_bucket", self.base_path)

    def _save_file(self, data, filename):
        s3 = utils.get_s3()
        self.base_path = uuid.uuid4().hex
        bucket = self.base_path

        # Create bucket if it doesn't exist yet.
        if s3.Bucket(bucket) not in s3.buckets.all():
            s3.create_bucket(Bucket=bucket)
        else:
            raise ValidationError("Bucket already exists")

        s3.Bucket(bucket).Object(self.data.filename).put(Body=data.read())

        return self.data.filename
