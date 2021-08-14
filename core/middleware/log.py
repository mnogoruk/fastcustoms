import logging
import random
import re
import string

from django.urls import resolve, Resolver404
from django.conf import settings

DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_HTTP_4XX_LOG_LEVEL = logging.ERROR
DEFAULT_COLORIZE = True
DEFAULT_SENSITIVE_HEADERS = [
    "Authorization", "Proxy-Authorization"
]
SETTING_NAMES = {
    "log_level": "REQUEST_LOGGING_DATA_LOG_LEVEL",
    "http_4xx_log_level": "REQUEST_LOGGING_HTTP_4XX_LOG_LEVEL",
    "max_body_length": "REQUEST_LOGGING_MAX_BODY_LENGTH",
    "sensitive_headers": "REQUEST_LOGGING_SENSITIVE_HEADERS",
}

NO_LOGGING_ATTR = "no_logging"
NO_LOGGING_MSG_ATTR = "no_logging_msg"
NO_LOGGING_MSG = "No logging for this endpoint"
request_logger = logging.getLogger("django.request")


def generate_log_unique():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9))


class Logger:
    def __init__(self, logger_unique=generate_log_unique()):
        self.logger_unique = logger_unique

    def log(self, level, msg, logging_context):
        args = logging_context["args"]
        kwargs = logging_context["kwargs"]
        for line in re.split(r"\r?\n", str(msg)):
            request_logger.log(level, f'{line} | [{self.logger_unique}]', *args, **kwargs)

    def log_error(self, level, msg, logging_context):
        self.log(level, msg, logging_context)


class LoggingMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

        self.log_level = getattr(settings, SETTING_NAMES["log_level"], DEFAULT_LOG_LEVEL)
        self.http_4xx_log_level = getattr(settings, SETTING_NAMES["http_4xx_log_level"], DEFAULT_HTTP_4XX_LOG_LEVEL)
        self.sensitive_headers = getattr(settings, SETTING_NAMES["sensitive_headers"], DEFAULT_SENSITIVE_HEADERS)
        if not isinstance(self.sensitive_headers, list):
            raise ValueError(
                "{} should be list. {} is not list.".format(SETTING_NAMES["sensitive_headers"], self.sensitive_headers)
            )

        for log_attr in ("log_level", "http_4xx_log_level"):
            level = getattr(self, log_attr)
            if level not in [
                logging.NOTSET,
                logging.DEBUG,
                logging.INFO,
                logging.WARNING,
                logging.ERROR,
                logging.CRITICAL,
            ]:
                raise ValueError("Unknown log level({}) in setting({})".format(level, SETTING_NAMES[log_attr]))

        self.logger = Logger()
        self.boundary = ""
        self.cached_request_body = None

    def __call__(self, request):
        self.cached_request_body = request.body
        response = self.get_response(request)
        self.logger.logger_unique = generate_log_unique()
        self.process_request(request, response)
        self.process_response(request, response)

        return response

    def process_request(self, request, response=None):
        skip_logging, because = self._should_log_route(request)
        if skip_logging:
            if because is not None:
                return self._skip_logging_request(request, because)
        else:
            return self._log_request(request, response)

    def _should_log_route(self, request):
        # request.urlconf may be set by middleware or application level code.
        # Use this urlconf if present or default to None.
        # https://docs.djangoproject.com/en/2.1/topics/http/urls/#how-django-processes-a-request
        # https://docs.djangoproject.com/en/2.1/ref/request-response/#attributes-set-by-middleware
        urlconf = getattr(request, "urlconf", None)

        try:
            route_match = resolve(request.path, urlconf=urlconf)
        except Resolver404:
            return False, None

        method = request.method.lower()
        view = route_match.func
        func = view
        # This is for "django rest framework"
        if hasattr(view, "cls"):
            if hasattr(view, "actions"):
                actions = view.actions
                method_name = actions.get(method)
                if method_name:
                    func = getattr(view.cls, view.actions[method], None)
            else:
                func = getattr(view.cls, method, None)
        elif hasattr(view, "view_class"):
            # This is for django class-based views
            func = getattr(view.view_class, method, None)
        no_logging = getattr(func, NO_LOGGING_ATTR, False)
        no_logging_msg = getattr(func, NO_LOGGING_MSG_ATTR, None)
        return no_logging, no_logging_msg

    def _skip_logging_request(self, request, reason):
        method_path = "{} {}".format(request.method, request.get_full_path())
        no_log_context = {
            "args": (),
            "kwargs": {"extra": {"no_logging": reason}},
        }
        self.logger.log(logging.INFO, method_path + " (not logged because '" + reason + "')", no_log_context)

    def _log_request(self, request, response):
        method_path = "{} {}".format(request.method, request.get_full_path())
        logging_context = self._get_logging_context(request, None)

        # Determine log level depending on response status
        log_level = self.log_level
        if response is not None:
            if response.status_code in range(400, 500):
                log_level = self.http_4xx_log_level
            elif response.status_code in range(500, 600):
                log_level = logging.ERROR

        self.logger.log(logging.INFO, method_path, logging_context)
        self._log_request_headers(request, logging_context, log_level)
        self._log_request_body(request, logging_context, log_level)

    def _log_request_headers(self, request, logging_context, log_level):
        headers = {k: v if k not in self.sensitive_headers else "*****" for k, v in request.headers.items()}

        if headers:
            self.logger.log(log_level, headers, logging_context)

    def _log_request_body(self, request, logging_context, log_level):
        if self.cached_request_body is not None:
            self.logger.log(log_level, self.cached_request_body, logging_context)

    def process_response(self, request, response):
        resp_log = "{} {} - {}".format(request.method, request.get_full_path(), response.status_code)
        skip_logging, because = self._should_log_route(request)
        if skip_logging:
            if because is not None:
                self.logger.log_error(
                    logging.INFO, resp_log, {"args": {}, "kwargs": {"extra": {"no_logging": because}}}
                )
            return response
        logging_context = self._get_logging_context(request, response)

        if response.status_code in range(400, 500):
            self.logger.log(self.http_4xx_log_level, resp_log, logging_context)
            self._log_resp(self.log_level, response, logging_context)
        elif response.status_code in range(500, 600):
            self.logger.log_error(logging.INFO, resp_log, logging_context)
            self._log_resp(logging.ERROR, response, logging_context)

        return response

    def _get_logging_context(self, request, response):
        """
        Returns a map with args and kwargs to provide additional context to calls to logging.log().
        This allows the logging context to be created per process request/response call.
        """
        return {
            "args": (),
            "kwargs": {"extra": {"request": request, "response": response}},
        }

    def _log_resp(self, level, response, logging_context):
        if re.match("^application/json", response.get("Content-Type", ""), re.I):
            response_headers = response.headers
            self.logger.log(level, response_headers, logging_context)
            self.logger.log(level, response.content, logging_context)
