import os
import pytest
import src.libs.curated_app_libs

yaml_file_name = "tests_with_attestation.yaml"
tests_yaml_path = os.path.join(os.getcwd(), 'data', yaml_file_name)

class TestClass:

    def test_redis_with_attestation(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    def test_pytorch_with_attestation(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    def test_redis_with_attestation_cert_file(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    def test_redis_with_attestation_cert_file_runtime_variables(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    def test_redis_with_attestation_end_test_ssl_path(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result
    
    def test_redis_with_attestation_sign_key(self):
        test_result = src.libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result
    
