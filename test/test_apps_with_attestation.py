import os
import pytest
import libs.curated_app_libs

yaml_file_name = "tests_with_attestation.yaml"
tests_yaml_path = os.path.join(os.getcwd(), 'data', yaml_file_name)

@pytest.mark.usefixtures("copy_repo")
@pytest.mark.usefixtures("curated_setup")
@pytest.mark.attestation
class TestClass:
    @pytest.mark.redis
    @pytest.mark.redis_attestation
    @pytest.mark.jenkins_runs
    def test_redis_with_attestation(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_attestation
    @pytest.mark.jenkins_runs
    def test_redis_with_test_attestation(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_attestation
    @pytest.mark.jenkins_runs
    def test_redis_with_attestation_local_image(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_attestation
    @pytest.mark.jenkins_runs
    def test_redis_with_attestation_runtime_variables(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_attestation
    def test_redis_with_attestation_end_test_ssl_path(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_attestation
    def test_redis_with_attestation_ssl_server_crt(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_attestation
    def test_redis_with_attestation_ssl_server_key(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_attestation
    def test_redis_with_attestation_wo_ssl(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.pytorch
    @pytest.mark.pytorch_attestation
    def test_pytorch_with_attestation_no_encryption_key(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.pytorch
    @pytest.mark.pytorch_attestation
    @pytest.mark.jenkins_runs
    def test_pytorch_with_attestation_encrypted_image(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.pytorch
    @pytest.mark.pytorch_attestation
    @pytest.mark.jenkins_runs
    def test_pytorch_with_test_attestation(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.pytorch
    @pytest.mark.pytorch_attestation
    @pytest.mark.jenkins_runs
    def test_pytorch_with_attestation_wrong_encrypted_list(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.pytorch
    @pytest.mark.pytorch_attestation
    @pytest.mark.jenkins_runs
    def test_pytorch_with_attestation_invalid_encrypted_files(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.pytorch
    @pytest.mark.pytorch_attestation
    @pytest.mark.jenkins_runs
    def test_pytorch_with_attestation_encrypted_file_invalid_format(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.pytorch
    @pytest.mark.pytorch_attestation
    @pytest.mark.jenkins_runs
    def test_pytorch_with_attestation_invalid_encryption_key(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.bash
    @pytest.mark.bash_attestation
    @pytest.mark.jenkins_runs
    def test_bash_with_test_attestation(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.bash
    @pytest.mark.bash_attestation
    @pytest.mark.jenkins_runs
    def test_bash_with_attestation(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.bash
    @pytest.mark.bash_attestation
    @pytest.mark.jenkins_runs
    def test_bash_attestation_without_verifier_image(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.pytorch
    @pytest.mark.pytorch_attestation
    def test_pytorch_with_test_option(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result
