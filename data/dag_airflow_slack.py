```
This DAG sends arise message to Slack.
```


from airflow import DAG
from airflow import AirflowException
from datetime import timedelta, datetime
from airflow.utils.dates import days_ago
from airflow.hooks.base_hook import BaseHook
from airflow.operators.python import PythonOperator
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator


# create connection in airflow
SLACK_CONN_ID = 'slack'


# arise message
def task_to_fail():
    raise AirflowException("Error msj")


# sending message 
def to_slack_bot(**kwargs):
    slack_webhook_token = BaseHook.get_connection(SLACK_CONN_ID).password
    slack_msg = """
            :red_circle: Task Failed. 
            *Task*: {task}  
            *Dag*: {dag} 
            *Execution Time*: {exec_date}  
            *Log Url*: {log_url} 
            """.format(
            task=kwargs.get('task_instance').task_id,
            dag=kwargs.get('task_instance').dag_id,
            ti=kwargs.get('task_instance'),
            exec_date=kwargs.get('execution_date'),
            # log_url=kwargs.get('task_instance').log_url,
            log_url=AirflowException("Error msj"),
        )
    failed_alert = SlackWebhookOperator(
        task_id='slack_test',
        http_conn_id='slack',
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username='airflow')
    return failed_alert.execute(context=task_to_fail)


dag = DAG(
    'bot_msg',
    start_date=datetime(2020, 1, 1),
    schedule_interval='@once')
    
send = PythonOperator(task_id='send_msg',
                      python_callable=to_slack_bot,
                      dag=dag)
