from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import List, Dict, Optional
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()


class KubernetesService:
    def __init__(self):
        try:
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes config")
        except:
            try:
                config.load_kube_config()
                logger.info("Loaded local Kubernetes config")
            except Exception as e:
                logger.warning("Failed to load Kubernetes config", error=str(e))
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
    
    async def get_pod_logs(
        self,
        namespace: str,
        pod_name: str,
        container: Optional[str] = None,
        tail_lines: int = 100,
        since_seconds: Optional[int] = None
    ) -> str:
        try:
            logs = self.v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container=container,
                tail_lines=tail_lines,
                since_seconds=since_seconds
            )
            return logs
        except ApiException as e:
            logger.error("Failed to get pod logs", error=str(e))
            raise Exception(f"Failed to get logs: {e.reason}")
    
    async def get_pod_status(self, namespace: str, pod_name: str) -> Dict:
        try:
            pod = self.v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            
            return {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "phase": pod.status.phase,
                "conditions": [
                    {
                        "type": c.type,
                        "status": c.status,
                        "reason": c.reason,
                        "message": c.message
                    }
                    for c in (pod.status.conditions or [])
                ],
                "container_statuses": [
                    {
                        "name": cs.name,
                        "ready": cs.ready,
                        "restart_count": cs.restart_count,
                        "state": self._get_container_state(cs.state)
                    }
                    for cs in (pod.status.container_statuses or [])
                ],
                "node_name": pod.spec.node_name,
                "start_time": pod.status.start_time.isoformat() if pod.status.start_time else None
            }
        except ApiException as e:
            logger.error("Failed to get pod status", error=str(e))
            raise Exception(f"Failed to get pod status: {e.reason}")
    
    def _get_container_state(self, state) -> Dict:
        if state.running:
            return {"status": "running", "started_at": state.running.started_at.isoformat()}
        elif state.waiting:
            return {"status": "waiting", "reason": state.waiting.reason, "message": state.waiting.message}
        elif state.terminated:
            return {
                "status": "terminated",
                "reason": state.terminated.reason,
                "exit_code": state.terminated.exit_code,
                "message": state.terminated.message
            }
        return {"status": "unknown"}
    
    async def list_pods(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None
    ) -> List[Dict]:
        try:
            if namespace:
                pods = self.v1.list_namespaced_pod(
                    namespace=namespace,
                    label_selector=label_selector
                )
            else:
                pods = self.v1.list_pod_for_all_namespaces(
                    label_selector=label_selector
                )
            
            return [
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "phase": pod.status.phase,
                    "node": pod.spec.node_name,
                    "restarts": sum(
                        cs.restart_count for cs in (pod.status.container_statuses or [])
                    )
                }
                for pod in pods.items
            ]
        except ApiException as e:
            logger.error("Failed to list pods", error=str(e))
            return []
    
    async def get_events(
        self,
        namespace: Optional[str] = None,
        field_selector: Optional[str] = None
    ) -> List[Dict]:
        try:
            if namespace:
                events = self.v1.list_namespaced_event(
                    namespace=namespace,
                    field_selector=field_selector
                )
            else:
                events = self.v1.list_event_for_all_namespaces(
                    field_selector=field_selector
                )
            
            return [
                {
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "object": f"{event.involved_object.kind}/{event.involved_object.name}",
                    "namespace": event.metadata.namespace,
                    "timestamp": event.last_timestamp.isoformat() if event.last_timestamp else None
                }
                for event in events.items
            ]
        except ApiException as e:
            logger.error("Failed to get events", error=str(e))
            return []
    
    async def get_deployment_status(self, namespace: str, deployment_name: str) -> Dict:
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            return {
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "replicas": deployment.spec.replicas,
                "ready_replicas": deployment.status.ready_replicas or 0,
                "available_replicas": deployment.status.available_replicas or 0,
                "updated_replicas": deployment.status.updated_replicas or 0,
                "conditions": [
                    {
                        "type": c.type,
                        "status": c.status,
                        "reason": c.reason,
                        "message": c.message
                    }
                    for c in (deployment.status.conditions or [])
                ]
            }
        except ApiException as e:
            logger.error("Failed to get deployment status", error=str(e))
            raise Exception(f"Failed to get deployment status: {e.reason}")


kubernetes_service = KubernetesService()
