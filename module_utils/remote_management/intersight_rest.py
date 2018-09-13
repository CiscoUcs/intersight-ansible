"""
Intersight REST API Module
Author: Matthew Garrett
Contributors: David Soper, Chris Gascoigne, John McDonough
Email: mgarrett0402@gmail.com

Copyright (c) 2018 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at:

             https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

from base64 import b64encode
from email.utils import formatdate
from six.moves.urllib.parse import urlparse, urlencode, quote

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

import requests
import json

host = 'https://intersight.com/api/v1'
digest_algorithm = 'rsa-sha256'

private_key = None
public_key = None

def set_public_key(pub_key):
    """
    Set RSA public key

    :param pub_key: rsa public key string
    """

    global public_key

    public_key = pub_key

def set_private_key(prv_key):
    """
    Set RSA private key

    :param pub_key: rsa private key string
    """

    global private_key

    private_key = prv_key

def get_sha256_digest(data):
    """
    Generates a SHA256 digest from a String.

    :param data: data string set by user
    :return: instance of digest object
    """
    digest = SHA256.new()
    digest.update(data)

    return digest

def get_rsasig_b64encode(digest):
    """
    Generates an RSA Signed SHA256 digest from a String

    :param digest: string to be signed & hashed
    :return: instance of digest object
    """

    rsakey = RSA.importKey(private_key)
    signer = PKCS1_v1_5.new(rsakey)
    sign = signer.sign(digest)

    return b64encode(sign)

def get_auth_header(hdrs, signed_msg):
    """
    Assmebled an Intersight formatted authorization header

    :param hdrs : object with header keys
    :param signed_msg: base64 encoded sha256 hashed body
    :return: concatenated authorization header
    """

    auth_str = ""
    auth_str = auth_str + "Signature"

    auth_str = auth_str + " " + "keyId=\"" + public_key + "\"," + "algorithm=\"" + digest_algorithm + "\"," + "headers=\"(request-target)"

    for key, _ in hdrs.items():
        auth_str = auth_str + " " + key.lower()
    auth_str = auth_str + "\""

    auth_str = auth_str + "," + "signature=\"" + signed_msg.decode('ascii') + "\""

    return auth_str

def prepare_str_to_sign(req_tgt, hdrs):
    """
    Concatenates Intersight headers in preparation to be RSA signed

    :param req_tgt : http method plus endpoint
    :param hdrs: dict with header keys
    :return: concatenated header authorization string
    """
    ss = ""
    ss = ss + "(request-target): " + req_tgt.lower() + "\n"

    length = len(hdrs.items())

    i = 0
    for key, value in hdrs.items():
        ss = ss + key.lower() + ": " + value
        if i < length-1:
            ss = ss + "\n"
        i += 1

    return ss

def get_moid_by_name(resource_path, target_name):
    """
    Retrieve an Intersight object moid by name

    :param resource_path: intersight resource path e.g. '/ntp/Policies'
    :param target_name: intersight object name
    :return: json http response object
    """
    query_params = {
        "$filter": "Name eq '{0}'".format(target_name)
    }

    options = {
        "http_method": "GET",
        "resource_path": resource_path,
        "query_params": query_params
    }

    get_moid = intersight_call(**options)

    if(get_moid.json()['Results'] != None):
        located_moid = get_moid.json()['Results'][0]['Moid']
    else:
        raise KeyError('Object with name "{0}" not found!'.format(target_name))

    return located_moid

def get_gmt_date():
    """
    Generated a GMT formatted Date

    :return: current date
    """

    return formatdate(timeval=None, localtime=False, usegmt=True)

def intersight_call(http_method="", resource_path="", query_params={}, body={}, moid=None, name=None):
    """
    Invoke the Intersight API

    :param resource_path: intersight resource path e.g. '/ntp/Policies'
    :param query_params: dictionary object with query string parameters as key/value pairs
    :param body: dictionary object with intersight data
    :param moid: intersight object moid
    :param name: intersight object name
    :return: json http response object
    """

    target_host = urlparse(host).netloc
    target_path = urlparse(host).path
    query_path = ""
    method = http_method.upper()

    # Verify an accepted HTTP verb was chosen
    if(method not in ['GET','POST','PATCH','DELETE']):
        raise ValueError('Please select a valid HTTP verb (GET/POST/PATCH/DELETE)')

    # Verify the resource path isn't empy & is a valid String
    if(resource_path != "" and type(resource_path) is not str):
        raise TypeError('The *resource_path* value is required and must be of type "String"')

    # Verify the query parameters isn't empy & is a valid Javascript Object
    if(query_params != {} and type(query_params) is not dict):
        raise TypeError('The *query_params* value must be of type "Object"')

    # Verify the body isn't empy & is a valid Javascript Object
    if(body != {} and type(body) is not dict):
        raise TypeError('The *body* value must be of type "Object"')

    # Verify the MOID is not null & of proper length
    if(moid != None and len(moid.encode('utf-8')) != 24):
        raise ValueError('Invalid *moid* value!')

    # Verify the public key is set
    if(public_key == None):
        raise ValueError('Public Key not set!')

    # Verify the private key is set
    if(private_key == None):
        raise ValueError('Private Key not set!')

    # Check for query_params, encode, and concatenate onto URL
    if(query_params != {}):
        query_path = "?" + urlencode(query_params, quote_via=quote)

    # Handle PATCH/DELETE by Object "name" instead of "moid"
    if(method == "PATCH" or method == "DELETE"):
        if(moid == None):
            if(name != None):
                if(type(name) is str):
                    moid = get_moid_by_name(resource_path, name)
                else:
                    raise TypeError('The *name* value must be of type "String"')
            else:
                raise ValueError('Must set either *moid* or *name* with "PATCH/DELETE!"')

    # Check for moid and concatenate onto URL
    if(method != "POST" and moid != None):
        resource_path += "/" + moid

    # Concatenate URLs for headers
    target_url = host + resource_path
    request_target = method + " " + target_path + resource_path + query_path

    # Get the current GMT Date/Time
    cdate = get_gmt_date()

    # Generate the body digest
    body_digest = get_sha256_digest(json.dumps(body).encode())
    b64_body_digest = b64encode(body_digest.digest())

    # Generate the authorization header
    auth_header = {
        'Date' : cdate,
        'Host' : target_host,
        'Digest' : "SHA-256=" + b64_body_digest.decode('ascii')
    }

    string_to_sign = prepare_str_to_sign(request_target, auth_header)
    auth_digest = get_sha256_digest(string_to_sign.encode())
    b64_signed_msg = get_rsasig_b64encode(auth_digest)
    auth_header = get_auth_header(auth_header, b64_signed_msg)

    # Generate the HTTP requests header
    request_header = {
        'Accept':           'application/json',
        'Host':             '{0}'.format(target_host),
        'Date':             '{0}'.format(cdate),
        'Digest':           'SHA-256={0}'.format(b64_body_digest.decode('ascii')),
        'Authorization':    '{0}'.format(auth_header),
    }

    # Format HTTP request
    http_request = requests.Request(
        method = method,
        url = target_url,
        headers = request_header,
        json = body,
        params = urlencode(query_params, quote_via=quote)
    )

    # Prepare & send HTTP request
    prepared_request = http_request.prepare()
    http_session = requests.Session()
    response = http_session.send(prepared_request)

    # Return requests.Response
    return response
