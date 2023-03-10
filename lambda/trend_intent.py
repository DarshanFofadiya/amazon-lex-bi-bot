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


# SELECT statement for Trend query
TREND_SELECT = "SELECT sum(net_ordered_gms_wk9) as gms_curr_week, sum(net_ordered_gms_wk8) as gms_curr_weekminus1, sum(net_ordered_gms_wk7) as gms_curr_weekminus2, sum(net_ordered_gms_wk6) as gms_curr_weekminus3 from scenario1"
TREND_WHERE_AM = " where am = {}"
TREND_WHERE_MERCHANT = " where merchant_customer_id = {}"


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
        return trend_intent_handler(event, session_attributes)


def trend_intent_handler(intent_request, session_attributes):
    method_start = time.perf_counter()
    
    logger.debug('<<BIBot>> trend_intent_handler: session_attributes = ' + json.dumps(session_attributes))

    session_attributes['greetingCount'] = '1'
    session_attributes['resetCount'] = '0'
    session_attributes['finishedCount'] = '0'
    session_attributes['lastIntent'] = 'Trend_Intent'

    # Retrieve slot values from the current request
    slot_values = session_attributes.get('slot_values')
    
    try:
        slot_values = helpers.get_slot_values(slot_values, intent_request)
    except bibot.SlotError as err:
        return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': str(err)})   
        
    logger.debug('<<BIBot>> "trend_intent_handler(): slot_values: %s', slot_values)

    #check if merchant slot is present then delete am slot

    if slot_values.get('merchant') is not None:
        delete_am_slot = True
    # Retrieve "remembered" slot values from session attributes
    slot_values = helpers.get_remembered_slot_values(slot_values, session_attributes)
    logger.debug('<<BIBot>> "count_intent_handler(): slot_values afer get_remembered_slot_values: %s', slot_values)

    if delete_am_slot:
        slot_values['am'] = None

    if slot_values.get('merchant') is None and slot_values.get('am') is None:
        return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText', 'content':
            str("Please say something like: Show me trend for am Huuchid or \n Show me trend for merchant 513008907002")})

    #if am slot is provided forget the merchant slot
    if slot_values.get('am') is not None:
        slot_values['merchant'] = None

    # Remember updated slot values
    helpers.remember_slot_values(slot_values, session_attributes)

    # Build and execute query
    select_clause = TREND_SELECT

    if slot_values.get('merchant') is not None:
        where_clause = TREND_WHERE_MERCHANT.format(("'" + slot_values.get('merchant') + "'"))
    else:
        where_clause = TREND_WHERE_AM.format(("'" + slot_values.get('am') + "'"))

    query_string = select_clause + where_clause
    
    logger.debug('<<BIBot>> Athena Query String = ' + query_string)  

    try:
        response = helpers.execute_athena_query(query_string)
    except:
        response = "Error"

    if response != "Error":
        if slot_values.get('merchant') is not None:
            response_string = 'The last 4 week GMS trend for merchant_id {} is \n'.format(slot_values.get('merchant'))
        else:
            response_string = 'The last 4 week GMS trend for AM {} is \n'.format(slot_values.get('am'))

    result_count = len(response['ResultSet']['Rows']) - 1

    if result_count > 0:
        str_op = "\n GMS Current Week: {} \n, GMS Current Week-1: {} \n , GMS Current Week-2: {} \n , GMS Current Week-3: {} \n"
        row_data = response['ResultSet']['Rows'][1]['Data']
        str_op = str_op.format(row_data[0]['VarCharValue'], row_data[1]['VarCharValue'], row_data[2]['VarCharValue'], row_data[3]['VarCharValue'])
        response_string += '\n'
        response_string += str_op

    logger.debug('<<BIBot>> response_string = ' + response_string) 

    method_duration = time.perf_counter() - method_start
    method_duration_string = 'method time = %.0f' % (method_duration * 1000) + ' ms'
    logger.debug('<<BIBot>> "Method duration is: ' + method_duration_string) 

    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   

