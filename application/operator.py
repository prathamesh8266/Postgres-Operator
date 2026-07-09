import kopf

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

# Load cluster credentials.
# If the operator runs inside Kubernetes, this loads the ServiceAccount token.
# If you're testing locally, use load_kube_config() instead.
try:
    config.load_incluster_config()
    print("Running inside Kubernetes")
except config.ConfigException:
    config.load_kube_config()
    print("Running locally")

apps = client.AppsV1Api()
core = client.CoreV1Api()

# starts the reconciliation loop, Kubernetes sends an event ADDED to Kopf.
# Kopf then calls this function.
# This function is one entry point into the reconciliation process.
@kopf.on.create("database.example.com", "v1", "postgreses")
def create_fn(spec, name, namespace, **kwargs):
        reconcile(spec, name, namespace)


# If storage changes
# 5Gi
# ↓
# 10Gi
# this function executes.
@kopf.on.update("database.example.com", "v1", "postgreses")
def update_fn(spec, name, namespace, **kwargs):
        reconcile(spec, name, namespace)


@kopf.on.delete("database.example.com", "v1", "postgreses")
def delete_fn(spec,name, namespace, **kwargs):
        print(f"Deleting {name}")


# Better Approach
# Rather than duplicate logic, every event should call one function:
# Create Event
#         │
#         ▼
#    reconcile()

# Update Event
#         │
#         ▼
#    reconcile()

# Resume Event
#         │
#         ▼
#    reconcile()

# Periodic Event
#         │
#         ▼
#    reconcile()


# Notice there is no while loop here 
# Because Kopf provides the event loop. Kubernetes events (create/update/delete/resume/timers) trigger reconcile(). 
# In lower-level controller implementations, there is an explicit work queue and loop, but Kopf hides that complexity.
def reconcile(spec, name, namespace):

    """
    Every reconciliation tries to make the actual cluster
    match the desired state described by the Postgres CR.

    Desired state:
        spec.image = postgres:16
        spec.storage = 5Gi

    Current state:
        Maybe no StatefulSet exists yet,
        or the image is outdated.

    The controller compares the two and makes the minimum
    required changes until they match.
    """

    # Check whether the StatefulSet already exists.
    try:
        apps.read_namespaced_stateful_set(
            name=name,
            namespace=namespace,
        )
        exists = True

    except ApiException as e:
        if e.status == 404:
            exists = False
        else:
            raise

    if not exists:
        create_statefulset(spec, name, namespace)

    
def create_statefulset(spec, name, namespace):
    statefulset = client.V1StatefulSet(
        metadata=client.V1ObjectMeta(
            name=name
        ),
        spec=client.V1StatefulSetSpec(
            service_name=name,
            replicas=1,
            selector=client.V1LabelSelector(
                match_labels={
                    "app": name
                }
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": name}
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="postgres",
                            image=spec["image"],

                            env=[
                                client.V1EnvVar(
                                    name="POSTGRES_USER",
                                    value=spec["username"],
                                ),
                                client.V1EnvVar(
                                    name="POSTGRES_PASSWORD",
                                    value=spec["password"],
                                ),
                                client.V1EnvVar(
                                    name="POSTGRES_DB",
                                    value=spec["database"],
                                ),
                            ],

                            ports=[
                                client.V1ContainerPort(
                                    container_port=5432,
                                )
                            ],
                        )
                    ]
                )
            )
        )
    )

    apps.create_namespaced_stateful_set(
        namespace=namespace,
        body=statefulset,
    )
    