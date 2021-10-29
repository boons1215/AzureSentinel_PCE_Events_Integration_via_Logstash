import requests, datetime, os
from requests.models import HTTPBasicAuth
from time import sleep

api_url = "https://scp4.illum.io/"
site_response = requests.get(api_url)

api_user='<api_user>'
api_key='<api_secret>'

current_hour_rfc_3339 = datetime.datetime.utcnow().isoformat("T") + "Z"
#last_hour = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
last_hour = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
last_hour_rfc_3339 = last_hour.isoformat("T") + "Z"
# local_path = "/var/log/"
local_path = ""
event_file = "illumio_events_data.json"
traffic_file = "illumio_traffic_data.csv"

# query the last hour PCE event data
def event_data_get():
    event_query = requests.get(
        api_url + 'api/v2/orgs/8/events',
        params='timestamp[gte]=' + last_hour_rfc_3339,
        auth=HTTPBasicAuth(api_user, api_key))

    if event_query.status_code == 200:
        with open(local_path + event_file, 'a', encoding = 'utf-8') as f:
            f.write(str(event_query.json()))
            f.write("\n")
    else:
        print('Failed to get event: ', event_query.status_code)

# create explorer last hour data search
def traffic_data_post():
    payload = {
        "sources": {
            "include": [
            []
            ],
            "exclude": []
        },
        "destinations": {
            "include": [
            []
            ],
            "exclude": []
        },
        "services": {
            "include": [],
            "exclude": []
        },
        "sources_destinations_query_op": "and",
        "start_date": last_hour_rfc_3339,
        "end_date": current_hour_rfc_3339,
        "policy_decisions": [],
        "max_results": 200000,
        "query_name": "traffic_data_thru_api"
    }

    post_job = requests.post(
        api_url + 'api/v2/orgs/8/traffic_flows/async_queries', json=payload,
        auth=HTTPBasicAuth(api_user, api_key))

    return post_job.status_code

# retrieve the explorer search href
def traffic_data_get(post_job_status):
    if post_job_status == 202:
        explorer_query_get = requests.get(
            api_url + 'api/v2/orgs/8/traffic_flows/async_queries', 
            auth=HTTPBasicAuth(api_user, api_key))
    else:
        print('Failed to get data: ', post_job_status)

    explorer_query_get = explorer_query_get.json()
    query_href = explorer_query_get[-1]['href']
    query_status = explorer_query_get[-1]['status']

    # monitoring the job, make sure it is completed
    while not (query_status == "completed"):
        sleep(2)
        explorer_query_status = requests.get(
            api_url + 'api/v2' + query_href, 
            auth=HTTPBasicAuth(api_user, api_key))

        query = explorer_query_status.json()
        query_status = query['status']

    return query_href

# download the completed data
def traffic_data_download(query_href):
    explorer_download = requests.get(
        api_url + 'api/v2' + query_href + '/download', 
        auth=HTTPBasicAuth(api_user, api_key))

    if explorer_download.status_code == 200:
        with open(local_path + traffic_file, 'w', encoding = 'utf-8') as csv_file:
            csv_file.write(explorer_download.text)
    else:
        print('Failed to download data: ', explorer_download.status_code)

if site_response.status_code == 200:
    # print(os.path.getsize(event_file))
    event_data_get()
    post_job_status = traffic_data_post()
    query_href = traffic_data_get(post_job_status)
    traffic_data_download(query_href)
