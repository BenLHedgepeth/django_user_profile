from os.path import join, dirname
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Profile


class ProfileInstanceMethods(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user('test_user')
        cls.image = open(
            join(dirname(__file__), 'images/test_image.jpg'), 'rb'
        )

        cls.profile_data = {
            'user': cls.test_user,
            'birth': '2019-01-01',
            'bio': 'Hello World!',
            'avatar': SimpleUploadedFile(
                cls.image.name,
                cls.image.read(),
                content_type="image/jpeg"
            )
        }

        cls.profile = Profile.objects.create(**cls.profile_data)

    def test_profile_str(self):
        self.assertEqual(str(self.profile), "Profile: test_user")

