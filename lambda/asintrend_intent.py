#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import time
import logging
import json
import bibot_config as bibot
import bibot_helpers as helpers
import bibot_userexits as userexits

TREND_SELECT = "select gms_curr_week, gms_curr_weekminus1, gms_curr_weekminus2, gms_curr_weekminus3, \
cast(cast(100*(cast(net_ordered_gms_wk10 as double)/net_ordered_gms_wk9 -1) as int) as varchar) || '%' as week_over_week \
from \
( \
select sum(net_ordered_gms_wk10) as net_ordered_gms_wk10, sum(net_ordered_gms_wk9) as net_ordered_gms_wk9, \
'$' || regexp_replace(cast(sum(net_ordered_gms_wk10) as VARCHAR), '(\d)(?=(\d\d\d)+(?!\d))', '$1,') as gms_curr_week, \
'$' || regexp_replace(cast(sum(net_ordered_gms_wk9) as VARCHAR), '(\d)(?=(\d\d\d)+(?!\d))', '$1,') as gms_curr_weekminus1, \
'$' || regexp_replace(cast(sum(net_ordered_gms_wk8) as VARCHAR), '(\d)(?=(\d\d\d)+(?!\d))', '$1,') as gms_curr_weekminus2, \
'$' || regexp_replace(cast(sum(net_ordered_gms_wk7) as VARCHAR), '(\d)(?=(\d\d\d)+(?!\d))', '$1,') as gms_curr_weekminus3 \
from eric_demo"

TREND_WHERE= " where asin = {} "

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    logger.debug('<<BIBot>> Lex event info = ' + json.dumps(event))

    session_attributes = event['sessionAttributes']
    logger.debug('<<BIBot>> lambda_handler: session_attributes = ' + json.dumps(session_attributes))

    config_error = helpers.get_bibot_config()
    if config_error is not None:
        return helpers.close(session_attributes, 'Fulfilled',
            {'contentType': 'PlainText', 'content': config_error})   
    else:
        return asintrend_intent_handler(event, session_attributes)


def asintrend_intent_handler(intent_request, session_attributes):
    method_start = time.perf_counter()
    
    logger.debug('<<BIBot>> trend_intent_handler: session_attributes = ' + json.dumps(session_attributes))

    session_attributes['greetingCount'] = '1'
    session_attributes['resetCount'] = '0'
    session_attributes['finishedCount'] = '0'
    session_attributes['lastIntent'] = 'Asintrend_Intent'

    # Retrieve slot values from the current request
    slot_values = session_attributes.get('slot_values')
    
    try:
        slot_values = helpers.get_slot_values(slot_values, intent_request)
    except bibot.SlotError as err:
        return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': str(err)})
    logger.debug('<<BIBot>> "Asintrend_intent_handler(): slot_values: %s', slot_values)

    # Retrieve "remembered" slot values from session attributes
    slot_values = helpers.get_remembered_slot_values(slot_values, session_attributes)
    logger.debug('<<BIBot>> "top_intent_handler(): slot_values afer get_remembered_slot_values: %s', slot_values)

    if slot_values.get('asin') is None:
        return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText', 'content':
            str("Please say something like: Show me trend for asin B00KTGEIXU")})

    # Remember updated slot values
    helpers.remember_slot_values(slot_values, session_attributes)

    # Build and execute query
    select_clause = TREND_SELECT
    where_clause = TREND_WHERE.format(("'" + slot_values.get('asin') + "'"))
    query_string = select_clause + where_clause + ")"
    logger.debug('<<BIBot>> Athena Query String = ' + query_string)


    try:
        response = helpers.execute_athena_query(query_string)
    except:
        response = "Error"

    if response != "Error":
        response_string = 'The last 4 week GMS trend for asin {} is \n'.format(slot_values.get('asin'))
    else:
        response_string = 'The query resulted in an error'

    result_count = len(response['ResultSet']['Rows']) - 1

    if result_count > 0:
        str_op = "\n GMS Current Week: {} \n, GMS Current Week-1: {} \n , GMS Current Week-2: {} \n , GMS Current Week-3: {} \n, GMS Current Week Over Week: {}"
        row_data = response['ResultSet']['Rows'][1]['Data']
        str_op = str_op.format(row_data[0]['VarCharValue'], row_data[1]['VarCharValue'], row_data[2]['VarCharValue'], row_data[3]['VarCharValue'], row_data[4]['VarCharValue'])
        response_string += '\n'
        response_string += str_op

    logger.debug('<<BIBot>> response_string = ' + response_string)

    method_duration = time.perf_counter() - method_start
    method_duration_string = 'method time = %.0f' % (method_duration * 1000) + ' ms'
    logger.debug('<<BIBot>> "Method duration is: ' + method_duration_string) 

    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   

