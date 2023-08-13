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
        image="pimenovdv/books-classifier:0.1.0",
        cmds=["python"],
        arguments=["./scripts/prepare_data.py", "--help"],
    )
