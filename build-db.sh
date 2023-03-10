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
    --query-string "create external table scenario1 (am STRING opportunity_id STRING stage STRING merchant_customer_id STRING marketplace_id int channel STRING gl STRING gl_product_group int net_ordered_gms_wk5 bigint net_ordered_gms_wk6 bigint net_ordered_gms_wk7 bigint net_ordered_gms_wk8 bigint net_ordered_units_wk5 bigint net_ordered_units_wk6 bigint net_ordered_units_wk7 bigint net_ordered_units_wk8 bigint net_shipped_gms_wk5 bigint net_shipped_gms_wk6 bigint net_shipped_gms_wk7 bigint net_shipped_gms_wk8 bigint net_shipped_units_wk5 bigint net_shipped_units_wk6 bigint net_shipped_units_wk7 bigint net_shipped_units_wk8 bigint buyable_asin_count_wk5 bigint buyable_asin_count_wk6 bigint buyable_asin_count_wk7 bigint buyable_asin_count_wk8 bigint asins_w_gv_wk5 bigint asins_w_gv_wk6 bigint asins_w_gv_wk7 bigint asins_w_gv_wk8 bigint) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' LOCATION '$ATHENA_BUCKET/scenario1';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null




