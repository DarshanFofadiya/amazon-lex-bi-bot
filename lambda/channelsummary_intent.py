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


# SELECT statement for Top query
TOP_SELECT = "select channel, '$' || regexp_replace(cast(sum(net_ordered_gms_wk8) as VARCHAR), '(\d)(?=(\d\d\d)+(?!\d))', '$1,') as net_ordered_gms from scenario1"
TOP_WHERE = " WHERE stage = 'Closed Won' and am = {}"
TOP_ORDERBY = " GROUP BY channel ORDER BY net_ordered_gms desc"


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
        return channelsummary_intent_handler(event, session_attributes)


def channelsummary_intent_handler(intent_request, session_attributes):
    method_start = time.perf_counter()

    logger.debug('<<BIBot>> top_intent_handler: session_attributes = ' + json.dumps(session_attributes))
    
    session_attributes['greetingCount'] = '1'
    session_attributes['resetCount'] = '0'
    session_attributes['finishedCount'] = '0'
    session_attributes['lastIntent'] = 'Channelsummary_Intent'

    # Retrieve slot values from the current request
    slot_values = session_attributes.get('slot_values')

    try:
        slot_values = helpers.get_slot_values(slot_values, intent_request)
    except bibot.SlotError as err:
        logger.debug("encountered an error in getting the slot values")
        return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': str(err)})   

    logger.debug('<<BIBot>> "top_intent_handler(): slot_values: %s', slot_values)

    # Retrieve "remembered" slot values from session attributes
    slot_values = helpers.get_remembered_slot_values(slot_values, session_attributes)
    logger.debug('<<BIBot>> "top_intent_handler(): slot_values afer get_remembered_slot_values: %s', slot_values)

    # store updated slot values
    logger.debug('<<BIBot>> "top_intent_handler(): calling remember_slot_values_NEW: %s', slot_values)
    helpers.remember_slot_values(slot_values, session_attributes)

    if slot_values.get('am') is None:
        response_string = 'Please tell me which AM do you want the summary for'
        return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   

    select_clause = TOP_SELECT

    try:
        where_clause = TOP_WHERE.format("'" + slot_values.get('am') + "'")
        order_by_clause = TOP_ORDERBY
    except KeyError:
        return helpers.close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': "Sorry, I couldn't fulfill your request. Please rephrase and try again providing the correct AM ID"
            }
        )  

    query_string = select_clause + where_clause + order_by_clause
    logger.debug('<<BIBot>> Athena Query String = ' + query_string)            

    # execute Athena query
    response = helpers.execute_athena_query(query_string)
    #logger.debug('Response from Athena is ', json.dumps(response))
    # Build response text for Lex
    response_string = 'The channelwise summary for {} is \n'.format(slot_values.get('am'))

    #formatting the output string
    str_op = ""
    for index, row in enumerate(response['ResultSet']['Rows']):
        if index != 0:
            str_op = str_op + row['Data'][0]['VarCharValue'] + " GMS : " + row['Data'][1]['VarCharValue']

            if index != len(response['ResultSet']['Rows']) - 1:
                str_op = str_op + " and "
    response_string += str_op

    logger.debug('<<BIBot>> response_string = ' + response_string) 

    method_duration = time.perf_counter() - method_start
    method_duration_string = 'method time = %.0f' % (method_duration * 1000) + ' ms'
    logger.debug('<<BIBot>> "Method duration is: ' + method_duration_string) 
    
    logger.debug('<<BIBot>> top_intent_handler() - sessions_attributes = %s, response = %s', session_attributes, {'contentType': 'PlainText','content': response_string})

    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   

