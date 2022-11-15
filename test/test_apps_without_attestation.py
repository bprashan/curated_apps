import os
import pytest
import libs.curated_app_libs

yaml_file_name = "tests_without_attestation.yaml"
tests_yaml_path = os.path.join(os.getcwd(), 'data', yaml_file_name)

@pytest.mark.usefixtures("copy_repo")
@pytest.mark.usefixtures("curated_setup")
@pytest.mark.non_attestation
class TestClass:
    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_default(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_default_with_debug(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_test_option(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_with_test_sign_key(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_with_test_sign_key_debug(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_with_runtime_variables(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_unknown_docker_image(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_empty_test_key(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_wrong_key_path(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    def test_redis_ra_wrong_option(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_ev_invalid_input_1(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    def test_redis_ev_dict(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_ev_invalid_input_2(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.bash
    @pytest.mark.bash_non_attestation
    @pytest.mark.jenkins_runs
    def test_bash_default(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.bash
    @pytest.mark.bash_non_attestation
    @pytest.mark.jenkins_runs
    def test_bash_runtime_args(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.bash
    @pytest.mark.bash_non_attestation
    @pytest.mark.jenkins_runs
    def test_bash_20_04_version(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    def test_commentary_sequence(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_protected_signing_key(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.redis
    @pytest.mark.redis_non_attestation
    @pytest.mark.jenkins_runs
    def test_redis_signing_key_no_input(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result
