import os
import pytest
import libs.curated_app_libs

yaml_file_name = "tests_latest_app_versions.yaml"
tests_yaml_path = os.path.join(os.getcwd(), 'data', yaml_file_name)

@pytest.mark.attestation
class TestClass:

    @pytest.mark.latest_apps
    @pytest.mark.redis
    @pytest.mark.redis_attestation
    def test_redis_latest_with_attestation(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result
    
    @pytest.mark.latest_apps
    @pytest.mark.ovms
    @pytest.mark.ovms_attestation
    def test_ovms_latest_with_attestation(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.latest_apps
    @pytest.mark.mariadb
    @pytest.mark.mariadb_attestation
    def test_mariadb_latest_with_attestation(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.latest_apps
    @pytest.mark.mysql
    @pytest.mark.mysql_attestation
    def test_mysql_latest_with_attestation(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result
    
    @pytest.mark.latest_apps
    @pytest.mark.pytorch
    @pytest.mark.pytorch_attestation
    def test_pytorch_latest_with_attestation(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.latest_apps
    @pytest.mark.sklearn
    @pytest.mark.sklearn_attestation
    def test_sklearn_latest_with_attestation(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.latest_apps
    @pytest.mark.memcached
    @pytest.mark.memcached_attestation
    def test_memcached_latest_with_attestation(self):
        test_result = libs.curated_app_libs.run_test(self, tests_yaml_path)
        assert test_result
