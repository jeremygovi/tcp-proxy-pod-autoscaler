from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from logger_toolbox import _logger


class KubernetesToolbox(object):

    _in_cluster: bool
    _configuration: config

    def __init__(self, _in_cluster=True):
        _logger.debug("START")
        self._in_cluster = _in_cluster
        self.load_kube_config()

    def load_kube_config(self):
        _logger.debug("START")
        if self._in_cluster:
            self._configuration = config.load_incluster_config()
        else:
            self._configuration = config.load_kube_config()

    # Deployments
    def get_deployment_annotation(self, _namespace, _deployment_name, _annotation):
        _logger.debug("START")
        with client.ApiClient(self._configuration) as api_client:
            api_instance = client.AppsV1Api(api_client)
            api_response = api_instance.read_namespaced_deployment(
                name=_deployment_name, namespace=_namespace)

        if _annotation in api_response.metadata.annotations:
            return api_response.metadata.annotations[_annotation]
        else:
            return None

    def get_deployment_status(self, _namespace, _deployment_name):
        _logger.debug("START")
        with client.ApiClient(self._configuration) as api_client:
            api_instance = client.AppsV1Api(api_client)
            api_response = api_instance.read_namespaced_deployment(
                name=_deployment_name, namespace=_namespace)

            if api_response.status.available_replicas > 0:
                return True

        return False
        # return api_response.status.replicas

    def get_deployment(self, _namespace, _deployment_name):
        _logger.debug("START")
        with client.ApiClient(self._configuration) as api_client:
            api_instance = client.AppsV1Api(api_client)

            try:
                api_response = api_instance.read_namespaced_deployment(
                    name=_deployment_name, namespace=_namespace)
            except ApiException as e:
                _logger.error(e)

            # _logger.info(f"{api_response=}")
            return api_response

    def get_replica_number(self, _namespace, _deployment_name):
        _logger.debug("START")
        with client.ApiClient(self._configuration) as api_client:
            api_instance = client.AppsV1Api(api_client)
            api_response = api_instance.read_namespaced_deployment(
                name=_deployment_name, namespace=_namespace)
            # _logger.debug(f"get_replica_number: {api_response =}")
            if api_response.status.available_replicas is None:
                return 0
            return api_response.status.available_replicas

        # return False
        # return api_response.status.replicas

    def update_deployment_annotation(self, _namespace, _deployment_name, _annotation, _annotation_value):
        _logger.debug("START")
        with client.ApiClient(self._configuration) as api_client:
            api_instance = client.AppsV1Api(api_client)

            # _deployment = self.get_deployment(_namespace, _deployment_name)
            # _deployment.metadata.annotations[_annotation] = _annotation_value
            _body = {"metadata": {"annotations": {
                f"{_annotation}": _annotation_value}}}

            try:
                api_response = api_instance.patch_namespaced_deployment(
                    name=_deployment_name, namespace=_namespace, body=_body, async_req=False)
            except ApiException as e:
                _logger.error(e)

    def update_replica_number(self, _namespace, _deployment_name, _replicas):
        _logger.debug("START")
        _logger.info(
            f"Updating replica number to {_replicas} due to traffic activity/inactivity")

        with client.ApiClient(self._configuration) as api_client:
            api_instance = client.AppsV1Api(api_client)

            _body = {"spec": {"replicas": _replicas}}
            try:
                api_response = api_instance.patch_namespaced_deployment(
                    name=_deployment_name, namespace=_namespace, body=_body, async_req=False)
            except ApiException as e:
                _logger.error(e)

    # Endpoints
    def check_endpoint_available(self, _namespace, _endpoint_name):
        _logger.debug("START")
        with client.ApiClient(self._configuration) as api_client:
            api_instance = client.CoreV1Api(api_client)
            api_response = api_instance.read_namespaced_endpoints(
                name=_endpoint_name, namespace=_namespace)
            # _logger.debug(f"check_endpoint_available: {api_response =}")
            if hasattr(api_response, 'subsets'):
                if hasattr(api_response.subsets, 'addresses'):
                    if len(api_response.subsets.addresses) > 0:
                        return True
            return False

    #     pass

    # Others

    # def watch_events(self):
    #     _logger.debug("START")
    #     # Configs can be set in Configuration class directly or using helper utility
    #     # config.load_kube_config()

    #     corev1 = client.CoreV1Api()
    #     networkv1 = client.NetworkingV1Api()
    #     count = 10
    #     w = watch.Watch()
    #     for event in w.stream(corev1.list_namespace, timeout_seconds=10):
    #         print("Event: %s %s" %
    #               (event['type'], event['object'].metadata.name))
    #         count -= 1
    #         if not count:
    #             w.stop()
    #     print("Finished namespace stream.")

    #     for event in w.stream(corev1.list_pod_for_all_namespaces, timeout_seconds=10):
    #         print("Event: %s %s %s" % (
    #             event['type'],
    #             event['object'].kind,
    #             event['object'].metadata.name)
    #         )
    #         count -= 1
    #         if not count:
    #             w.stop()
    #     print("Finished pod stream.")

    #     for event in w.stream(networkv1.list_ingress_for_all_namespaces, timeout_seconds=10):
    #         print("Event: %s %s %s" % (
    #             event['type'],
    #             event['object'].kind,
    #             event['object'].metadata.name)
    #         )
    #         count -= 1
    #         if not count:
    #             w.stop()
    #     print("Finished ingress stream.")
