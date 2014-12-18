import requests

class APIClient(object):
    verify_ssl_certs = False
    ssl_certs_path='./cert.crt'
    
    @classmethod
    def request(cls, method, resource, post_data=None):
        headers = {'Accept': 'application/json'}
        if (method == 'post') or (method == 'patch'):
            headers['Content-Type'] = 'application/json'
        import predicsis
        headers['Authorization'] = 'Bearer ' + predicsis.api_token;
        content, code, json = cls.request_full(method, predicsis.api_url + resource, headers, post_data)
        print code, content
        return cls._interpret_response(content, code, json)
        
    @classmethod
    def request_full(cls, method, url, headers, post_data=None):
        print method, url, headers, post_data
        kwargs = {}
        if cls.verify_ssl_certs:
            kwargs['verify'] = cls.ssl_certs_path
        else:
            kwargs['verify'] = False
            # requests.packages.urllib3.disable_warnings()
        try:
            try:
                result = requests.request(method, url, headers=headers, data=post_data, timeout=80, **kwargs)
            except TypeError, e:
                raise TypeError('Your "requests" library may be out of date. Error was: %s' % (e,))
            content = result.content
            status_code = result.status_code
            json = result.json()
        except Exception, e:
            cls._handle_request_error(e)
        return content, status_code, json
        
    @classmethod
    def _interpret_response(cls, content, code, json):
        if not (200 <= code < 300):
            cls._handle_api_error(content, code, json)
        return json
        
    @classmethod
    def _handle_api_error(cls, content, code, json):
        from predicsis import error
        raise error.PredicSisError(json['status'] +' '+ json['error'], content, code, json)
    
    @classmethod
    def _handle_request_error(cls, e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = ('Unexpected error communicating with PredicSis API. If this problem persists, let us know at support@predicsis.com.')
            err = "%s: %s" % (type(e).__name__, str(e))
        else:
            msg = ('Unexpected error communicating with PredicSis API (looks like a configuration issue). If this problem persists, let us know at support@predicsis.com.')
            err = "A %s was raised" % (type(e).__name__,)
        if str(e):
            err += " with error message %s" % (str(e),)
        else:
            err += " with no error message"
        msg = msg + "\n\n(Network error: %s)" % (err,)
        from predicsis import error
        raise error.PredicSisError(msg)