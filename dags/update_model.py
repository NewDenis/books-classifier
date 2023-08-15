from datetime import timedelta, datetime
from textwrap import dedent

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)

# Operators; we need this to operate!
from airflow.kubernetes.secret import Secret
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

# volume_mount = k8s.V1VolumeMount(
#     name="books-volume",
#     mount_path="/mnt/data",
#     sub_path=None,
# )

# volume = k8s.V1Volume(
#     name="books-volume",
#     persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
#         claim_name="books-volume"
#     ),
# )

secret_volumes = [
    Secret(
        deploy_type="volume",
        # Path where we mount the secret as volume
        deploy_target="/app/.dvc/",
        # Name of Kubernetes Secret
        secret="dvc-config",
        # Key in the form of service account file name
        key="config",
    ),
    Secret(
        deploy_type="volume",
        # Path where we mount the secret as volume
        deploy_target="/root/.aws/",
        # Name of Kubernetes Secret
        secret="aws-credentials",
        # Key in the form of service account file name
        key="credentials",
    ),
    Secret(
        deploy_type="env",
        # Path where we mount the secret as volume
        deploy_target="AWS_ACCESS_KEY_ID",
        # Name of Kubernetes Secret
        secret="aws-access-key-id",
        # Key in the form of service account file name
        key="aws-access-key-id",
    ),
    Secret(
        deploy_type="env",
        # Path where we mount the secret as volume
        deploy_target="AWS_SECRET_ACCESS_KEY",
        # Name of Kubernetes Secret
        secret="aws-secret-access-key",
        # Key in the form of service account file name
        key="aws-secret-access-key",
    ),
]

# tg_secrets = [
#     Secret(
#         deploy_type="env",
#         # Path where we mount the secret as volume
#         deploy_target="TG_CHAT_ID",
#         # Name of Kubernetes Secret
#         secret="tg-chat",
#         # Key in the form of service account file name
#         key="tg-chat",
#     ),
#     Secret(
#         deploy_type="env",
#         # Path where we mount the secret as volume
#         deploy_target="TG_TOKEN",
#         # Name of Kubernetes Secret
#         secret="tg-token",
#         # Key in the form of service account file name
#         key="tg-token",
#     ),
# ]


# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
with DAG(
    "update_model",
    description="Testing DAG",
    start_date=datetime.now(),
    # default_args={"run_as_user": "root"},
) as dag:
    # t1, t2 and t3 are examples of tasks created by instantiating operators
    t1 = KubernetesPodOperator(
        task_id="prepare_data",
        image="pimenovdv/books-classifier:0.2.12",
        cmds=["bash", "-cx"],
        arguments=["./scripts/prepare_data.sh"],
        image_pull_policy="Always",
        # volume_mounts=[volume_mount],
        # volumes=[volume],
        secrets=secret_volumes,
        startup_timeout_seconds=300,
    )

    t2 = KubernetesPodOperator(
        task_id="train_save",
        image="pimenovdv/books-classifier:0.2.12",
        # cmds=["cat"],
        # arguments=["/app/.dvc/config"],
        cmds=["bash", "-cx"],
        arguments=["./scripts/train_and_save.sh"],
        image_pull_policy="Always",
        # volume_mounts=[volume_mount],
        # volumes=[volume],
        secrets=secret_volumes,
        startup_timeout_seconds=300,
    )

    t1 >> t2
