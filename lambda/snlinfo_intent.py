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
        return snlinfo_intent_handler(event, session_attributes)


def snlinfo_intent_handler(intent_request, session_attributes):
    method_start = time.perf_counter()
    
    logger.debug('<<BIBot>> trend_intent_handler: session_attributes = ' + json.dumps(session_attributes))

    session_attributes['greetingCount'] = '1'
    session_attributes['resetCount'] = '0'
    session_attributes['finishedCount'] = '0'
    session_attributes['lastIntent'] = 'Snlinfo_Intent'

    # Retrieve slot values from the current request
    what_is_snl = "Small and Light (SnL) is a Fulfilment by Amazon (FBA) option for small, light and fast-moving ASINs which offers lower fulfilment fees versus standard FBA. Small and Light offers reduced fulfillment costs on eligible items, allowing you to pass the savings on to your customers. Signing up for Small and Light is easy and once Selling Partners have signed up, they will receive valuable benefits such as free shipping for Prime customers, reduced fulfilment fees and improved customer trust. Now SnL can be used in congruence with PanEU and EFN meaning ,if eligible, inventory can be distributed with Prime shipping by us across the whole of the EU."
    space_line = "                                                                                        "
    snl_eligibility = "ASINs fulfilling the following criteria can get enrolled into SnL: 1) in new condition 2) have dimensions less than or equal to 35 cm x 25 x 12cm 3) weigh less than 400g 4) are priced at €10 (DE) / €11 (FRITES) / £9 (UK) 5) are listed on the respective marketplace 6) age appropriate products, no over 18 years products not permitted 7) no Vape/Cigarette related products 8) no HAZMAT 9) no batteries 10) no personalized products 11) no temperature sensitive products"
    snl_price_de = "Pricing for SnL is as follows: 1) Small envelope 80g or less (20*15*1 cm or less) : SnL Price is 1.43 EUR and FBA Price is 2.14 EUR  2) Standard envelope 60g or less (33*23*2.5 cm or less) : SnL Price is 1.61 EUR and FBA Price is 2.33 EUR 3) Standard envelope 210g or less (33*23*2.5 cm or less) : SnL Price is 1.81 EUR and FBA Price is 2.47 EUR 4) Large envelope 225g or less (33*23*4 cm or less) : SnL Price is 2.52 EUR and FBA Price is 2.97 EUR 5) Extra large envelope 225g or less (33*23*6 cm or less) : SnL Price is 2.70 EUR and FBA Price is 3.35 EUR 6) Small parcel 150g or less (33*25*12 cm or less) : SnL Price is 3.09 EUR and FBA Price is 3.25 EUR 7) Small parcel 400g or less (33*25*12 cm or less) : SnL Price is 3.37 EUR and FBA Price is 3.58 EUR "

    response_string = what_is_snl + space_line + snl_eligibility + space_line + snl_price_de
    logger.debug('<<BIBot>> response_string = ' + response_string)

    method_duration = time.perf_counter() - method_start
    method_duration_string = 'method time = %.0f' % (method_duration * 1000) + ' ms'
    logger.debug('<<BIBot>> "Method duration is: ' + method_duration_string) 

    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   

