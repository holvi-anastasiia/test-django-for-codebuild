from django.test import TestCase

from .models import TestModel


class CodeBuildTest(TestCase):
    """
    "testing" TestCase 
    Verify that 
        a) we can create objects in dabaase
        b) we can get artefacts from codebuild
    """
    def test_is_ok(self):
        self.assertTrue(True)

    def test_db_usage(self):
        test_model = TestModel.objects.create(
            title='test')
        self.assertEqual(
            test_model.title, test)

    
    def test_is_not_ok(self):
        self.assertFalse(True)
