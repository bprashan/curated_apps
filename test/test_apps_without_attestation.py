import os
import pytest
import src.libs.curated_app_libs

yaml_file_name = "tests_without_attestation.yaml"
tests_yaml_path = os.path.join(os.getcwd(), 'data', yaml_file_name)


class TestClass:

    def test_redis_default(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    def test_redis_test_option(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    def test_redis_with_sign_key(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    def test_redis_with_runtime_variables(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result
    
    def test_redis_with_local_docker_image(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result
    
    def test_pytorch_default(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    def test_pytorch_test_option(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result
    
    def test_pytorch_with_local_docker_image(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    def test_redis_empty_test_key(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result