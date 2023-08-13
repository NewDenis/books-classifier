from datetime import timedelta, datetime
from textwrap import dedent

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

volume_mount = k8s.V1VolumeMount(
    name="books-volume",
    mount_path="/mnt/data",
    sub_path=None,
)

volume = k8s.V1Volume(
    name="books-volume",
    persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
        claim_name="books-volume"
    ),
)


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
        image="pimenovdv/books-classifier:0.2.0",
        cmds=["python"],
        arguments=["./scripts/prepare_data.py"],
        image_pull_policy="Always",
        volume_mounts=[volume_mount],
        volumes=[volume],
    )

    t2 = KubernetesPodOperator(
        task_id="train_save",
        image="pimenovdv/books-classifier:0.2.0",
        cmds=["python"],
        arguments=["./scripts/train_and_save.py"],
        image_pull_policy="Always",
        volume_mounts=[volume_mount],
        volumes=[volume],
    )

    t1 >> t2
