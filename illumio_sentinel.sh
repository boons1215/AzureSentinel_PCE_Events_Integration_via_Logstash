#!/usr/bin/env bash

api_user='<api_user>'
api_key='<api_secret>'
WorkingDirectory='/var/log'
ArchiveDirectory='/var/log/illumio_archive'

date_time=$(date --date="(date --rfc-3339=seconds) -10 minutes" '+%Y-%m-%dT%H:%M:%S.000Z')

if [ ! -d "$ArchiveDirectory" ]; then
  mkdir ${ArchiveDirectory}
fi

cp ${WorkingDirectory}/illumio_events.json ${ArchiveDirectory}/illumio_events_${date_time}.json &>2

curl -s -X GET https://scp4.illum.io:443/api/v2/orgs/<org_id>/events?timestamp[gte]=${date_time} -u ${api_user}:${api_key} -H 'Accept: application/json' >> ${WorkingDirectory}/illumio_events.json

echo "" >> ${WorkingDirectory}/illumio_events.json

echo "${date_time} Job Run" | tee -a ${WorkingDirectory}/illumio_cronjob

