#!/bin/bash

#
# Creates the Athena database
#

#
# Environment variables to be set in the CodeBuild project
#
# $ATHENA_DB    		Name of the Athena database
# $ATHENA_BUCKET		Name of the S3 bucket where the data is stored
# $ATHENA_BUCKET_REGION		Region for the S3 bucket where the data is stored
# $ATHENA_DB_DESCRIPTION	Description for the Athena database
#

echo "Starting build-db.sh"
echo '$ATHENA_DB' "= $ATHENA_DB"
echo '$ATHENA_BUCKET' "= $ATHENA_BUCKET"
echo '$ATHENA_BUCKET_REGION' "= $ATHENA_BUCKET_REGION"
echo '$ATHENA_DB_DESCRIPTION' "= $ATHENA_DB_DESCRIPTION"
echo

# Create TICKIT database
echo "Creating Athena database $ATHENA_DB"
aws glue create-database --database-input "Name=$ATHENA_DB,Description=$ATHENA_DB_DESCRIPTION" >/dev/null

# Create TICKIT scenario1 table in Athena
echo "Creating users table..."
aws athena start-query-execution \
    --query-string "create external table scenario1 (merchant_customer_id INT, channel STRING, gl STRING, gl_id INT, category STRING, net_ordered_gms_wk9 float, net_ordered_gms_wk8 float, net_ordered_gms_wk7 float, net_ordered_gms_wk6 float, am STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '$ATHENA_BUCKET/scenario1';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null




