from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для возврата ошибок в формате JSON.
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        error_data = {
            'error': True,
            'status_code': response.status_code,
            'detail': response.data,
        }
        
        if response.status_code >= 500:
            logger.error(f'API Error: {response.status_code} - {response.data}')
        else:
            logger.warning(f'API Warning: {response.status_code} - {response.data}')
        
        response.data = error_data
    
    return response