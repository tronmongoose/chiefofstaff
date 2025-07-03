"""
Production logging configuration for x402 Travel Booking System
Includes structured logging, error tracking, and performance monitoring
"""

import logging
import logging.handlers
import json
import time
import traceback
import os
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import requests

# Configure logging levels
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'environment': ENVIRONMENT,
            'service': 'x402-travel-planner'
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

class PerformanceLogger:
    """Performance monitoring and logging"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def log_request(self, method: str, path: str, status_code: int, duration: float, 
                   user_wallet: Optional[str] = None, payment_amount: Optional[str] = None):
        """Log HTTP request performance"""
        extra_fields = {
            'type': 'http_request',
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration_ms': round(duration * 1000, 2),
            'user_wallet': user_wallet,
            'payment_amount': payment_amount
        }
        
        level = logging.ERROR if status_code >= 400 else logging.INFO
        self.logger.log(level, f"{method} {path} - {status_code} ({duration:.3f}s)", 
                       extra={'extra_fields': extra_fields})
    
    def log_payment_event(self, event_type: str, amount: str, currency: str, 
                         wallet_address: str, success: bool, error: Optional[str] = None):
        """Log payment-related events"""
        extra_fields = {
            'type': 'payment_event',
            'event_type': event_type,
            'amount': amount,
            'currency': currency,
            'wallet_address': wallet_address,
            'success': success,
            'error': error
        }
        
        level = logging.ERROR if not success else logging.INFO
        self.logger.log(level, f"Payment {event_type}: {amount} {currency} - {'Success' if success else 'Failed'}", 
                       extra={'extra_fields': extra_fields})
    
    def log_database_operation(self, operation: str, table: str, duration: float, 
                              success: bool, error: Optional[str] = None):
        """Log database operations"""
        extra_fields = {
            'type': 'database_operation',
            'operation': operation,
            'table': table,
            'duration_ms': round(duration * 1000, 2),
            'success': success,
            'error': error
        }
        
        level = logging.ERROR if not success else logging.DEBUG
        self.logger.log(level, f"DB {operation} on {table} - {'Success' if success else 'Failed'} ({duration:.3f}s)", 
                       extra={'extra_fields': extra_fields})

class ErrorTracker:
    """Error tracking and reporting"""
    
    def __init__(self, logger, sentry_dsn: Optional[str] = None):
        self.logger = logger
        self.sentry_dsn = sentry_dsn
    
    def capture_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Capture and log exceptions with context"""
        extra_fields = {
            'type': 'exception',
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.logger.error(f"Exception: {type(exception).__name__}: {str(exception)}", 
                         extra={'extra_fields': extra_fields})
        
        # Send to Sentry if configured
        if self.sentry_dsn:
            self._send_to_sentry(exception, context)
    
    def _send_to_sentry(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Send error to Sentry (placeholder for actual Sentry integration)"""
        try:
            # This is a placeholder - in production, use the actual Sentry SDK
            sentry_data = {
                'message': str(exception),
                'level': 'error',
                'tags': {
                    'environment': ENVIRONMENT,
                    'service': 'x402-travel-planner'
                },
                'extra': context or {}
            }
            
            # Log that we would send to Sentry
            self.logger.info(f"Would send to Sentry: {json.dumps(sentry_data)}")
            
        except Exception as e:
            self.logger.error(f"Failed to send to Sentry: {e}")

def setup_logging() -> tuple[logging.Logger, PerformanceLogger, ErrorTracker]:
    """Setup production logging configuration"""
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Create main logger
    logger = logging.getLogger('x402-travel-planner')
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with structured formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredFormatter())
    logger.addHandler(console_handler)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(StructuredFormatter())
    logger.addHandler(error_handler)
    
    # Performance logger
    performance_logger = PerformanceLogger(logger)
    
    # Error tracker
    sentry_dsn = os.getenv('SENTRY_DSN')
    error_tracker = ErrorTracker(logger, sentry_dsn)
    
    logger.info("Logging system initialized", extra={
        'extra_fields': {
            'type': 'system_event',
            'event': 'logging_initialized',
            'log_level': LOG_LEVEL,
            'environment': ENVIRONMENT
        }
    })
    
    return logger, performance_logger, error_tracker

def log_function_performance(func):
    """Decorator to log function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('x402-travel-planner')
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.debug(f"Function {func.__name__} completed successfully", extra={
                'extra_fields': {
                    'type': 'function_performance',
                    'function': func.__name__,
                    'duration_ms': round(duration * 1000, 2),
                    'success': True
                }
            })
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(f"Function {func.__name__} failed", extra={
                'extra_fields': {
                    'type': 'function_performance',
                    'function': func.__name__,
                    'duration_ms': round(duration * 1000, 2),
                    'success': False,
                    'error': str(e)
                }
            })
            
            raise
    
    return wrapper

def log_api_request(func):
    """Decorator to log API request performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger('x402-travel-planner')
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Extract request info if available
            request_info = {}
            if args and hasattr(args[0], 'method'):
                request_info = {
                    'method': args[0].method,
                    'path': args[0].url.path,
                    'status_code': 200  # Assuming success
                }
            
            logger.info(f"API request completed", extra={
                'extra_fields': {
                    'type': 'api_request',
                    'duration_ms': round(duration * 1000, 2),
                    'success': True,
                    **request_info
                }
            })
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(f"API request failed", extra={
                'extra_fields': {
                    'type': 'api_request',
                    'duration_ms': round(duration * 1000, 2),
                    'success': False,
                    'error': str(e)
                }
            })
            
            raise
    
    return wrapper

# Initialize logging
logger, performance_logger, error_tracker = setup_logging()

# Export for use in other modules
__all__ = ['logger', 'performance_logger', 'error_tracker', 'log_function_performance', 'log_api_request'] 