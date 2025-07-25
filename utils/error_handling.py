import logging
import traceback
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import json
import threading
from enum import Enum
from config import config


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    API_ERROR = "api_error"
    PARSING_ERROR = "parsing_error"
    VALIDATION_ERROR = "validation_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    CONFIGURATION_ERROR = "configuration_error"
    DATA_QUALITY_ERROR = "data_quality_error"


@dataclass
class ErrorContext:
    timestamp: datetime
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    stack_trace: Optional[str]
    component: str
    user_context: Dict[str, Any]
    system_state: Dict[str, Any]
    suggested_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'error_id': self.error_id,
            'category': self.category.value,
            'severity': self.severity.value,
            'message': self.message,
            'stack_trace': self.stack_trace,
            'component': self.component,
            'user_context': self.user_context,
            'system_state': self.system_state,
            'suggested_actions': self.suggested_actions
        }


@dataclass
class SystemMetrics:
    timestamp: datetime
    component: str
    success_rate: float
    avg_response_time: float
    error_count: int
    total_requests: int
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None


class ErrorHandler:
    
    def __init__(self):
        self.errors: List[ErrorContext] = []
        self.metrics: List[SystemMetrics] = []
        self.error_patterns: Dict[str, int] = {}
        self.recovery_strategies: Dict[ErrorCategory, List[str]] = self._init_recovery_strategies()
        
        # Setup logging
        self._setup_logging()
        
        # Thread lock for concurrent access
        self._lock = threading.Lock()
    
    def _setup_logging(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Setup file handlers
        file_handler = logging.FileHandler('logs/resumeroast.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(detailed_formatter)
        
        error_handler = logging.FileHandler('logs/errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Setup main logger
        self.logger = logging.getLogger('ResumeRoast')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def _init_recovery_strategies(self) -> Dict[ErrorCategory, List[str]]:
        return {
            ErrorCategory.API_ERROR: [
                "Check API key validity and permissions",
                "Verify API endpoint availability",
                "Implement exponential backoff retry",
                "Switch to fallback AI model if available",
                "Use cached results if available"
            ],
            ErrorCategory.PARSING_ERROR: [
                "Validate input data format",
                "Use alternative parsing strategy",
                "Apply data cleaning and normalization",
                "Request manual data entry",
                "Use structured data fallback"
            ],
            ErrorCategory.NETWORK_ERROR: [
                "Check internet connectivity",
                "Retry with different user agent",
                "Use proxy or VPN if blocked",
                "Implement circuit breaker pattern",
                "Cache successful responses"
            ],
            ErrorCategory.TIMEOUT_ERROR: [
                "Increase timeout duration",
                "Break large requests into smaller chunks",
                "Implement async processing",
                "Add request queuing",
                "Use faster AI model"
            ],
            ErrorCategory.VALIDATION_ERROR: [
                "Validate input against schema",
                "Apply data sanitization",
                "Provide clear error messages to user",
                "Suggest valid input formats",
                "Use default values where appropriate"
            ]
        }
    
    def log_error(self, 
                 error: Exception,
                 category: ErrorCategory,
                 severity: ErrorSeverity,
                 component: str,
                 user_context: Dict[str, Any] = None,
                 system_state: Dict[str, Any] = None) -> str:
        
        error_id = f"{int(time.time())}-{hash(str(error)) % 10000}"
        
        error_context = ErrorContext(
            timestamp=datetime.now(),
            error_id=error_id,
            category=category,
            severity=severity,
            message=str(error),
            stack_trace=traceback.format_exc(),
            component=component,
            user_context=user_context or {},
            system_state=system_state or {},
            suggested_actions=self.recovery_strategies.get(category, [])
        )
        
        with self._lock:
            self.errors.append(error_context)
            
            # Track error patterns
            error_pattern = f"{category.value}:{type(error).__name__}"
            self.error_patterns[error_pattern] = self.error_patterns.get(error_pattern, 0) + 1
        
        # Log to file
        self.logger.error(f"[{error_id}] {component}: {error}", extra={
            'error_id': error_id,
            'category': category.value,
            'severity': severity.value,
            'user_context': user_context,
            'system_state': system_state
        })
        
        return error_id
    
    def log_metrics(self, component: str, success_rate: float, avg_response_time: float, 
                   error_count: int, total_requests: int):
        
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            component=component,
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            error_count=error_count,
            total_requests=total_requests
        )
        
        with self._lock:
            self.metrics.append(metrics)
        
        self.logger.info(f"Metrics for {component}: {success_rate:.1%} success, "
                        f"{avg_response_time:.2f}s avg response, "
                        f"{error_count}/{total_requests} errors")
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_errors = [e for e in self.errors if e.timestamp >= cutoff_time]
        
        if not recent_errors:
            return {
                'total_errors': 0,
                'error_rate': 0.0,
                'critical_errors': 0,
                'top_error_patterns': [],
                'affected_components': [],
                'recommendations': []
            }
        
        # Analyze error patterns
        error_by_category = {}
        error_by_severity = {}
        error_by_component = {}
        
        for error in recent_errors:
            # By category
            category = error.category.value
            error_by_category[category] = error_by_category.get(category, 0) + 1
            
            # By severity
            severity = error.severity.value
            error_by_severity[severity] = error_by_severity.get(severity, 0) + 1
            
            # By component
            component = error.component
            error_by_component[component] = error_by_component.get(component, 0) + 1
        
        # Generate recommendations
        recommendations = self._generate_recommendations(error_by_category, error_by_severity)
        
        return {
            'total_errors': len(recent_errors),
            'critical_errors': error_by_severity.get('critical', 0),
            'error_by_category': error_by_category,
            'error_by_severity': error_by_severity,
            'affected_components': list(error_by_component.keys()),
            'top_error_patterns': sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)[:5],
            'recommendations': recommendations
        }
    
    def _generate_recommendations(self, error_by_category: Dict[str, int], 
                                error_by_severity: Dict[str, int]) -> List[str]:
        recommendations = []
        
        # Check for high API error rate
        if error_by_category.get('api_error', 0) > 5:
            recommendations.append("High API error rate detected. Check API key validity and rate limits.")
        
        # Check for parsing issues
        if error_by_category.get('parsing_error', 0) > 3:
            recommendations.append("Multiple parsing errors detected. Review data validation and parsing logic.")
        
        # Check for network issues
        if error_by_category.get('network_error', 0) > 2:
            recommendations.append("Network connectivity issues detected. Consider implementing retry mechanisms.")
        
        # Check for critical errors
        if error_by_severity.get('critical', 0) > 0:
            recommendations.append("Critical errors detected. Immediate investigation required.")
        
        # General recommendations
        if sum(error_by_category.values()) > 10:
            recommendations.append("High error rate detected. Consider implementing circuit breaker pattern.")
        
        return recommendations
    
    def export_error_report(self, hours: int = 24, file_path: str = None) -> str:
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"logs/error_report_{timestamp}.json"
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [e for e in self.errors if e.timestamp >= cutoff_time]
        
        report = {
            'report_generated': datetime.now().isoformat(),
            'time_period_hours': hours,
            'summary': self.get_error_summary(hours),
            'detailed_errors': [error.to_dict() for error in recent_errors[-50:]]  # Last 50 errors
        }
        
        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return file_path
    
    def clear_old_errors(self, days: int = 7):
        cutoff_time = datetime.now() - timedelta(days=days)
        
        with self._lock:
            self.errors = [e for e in self.errors if e.timestamp >= cutoff_time]
            self.metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
        
        self.logger.info(f"Cleared errors older than {days} days")


class ComponentMonitor:
    
    def __init__(self, component_name: str, error_handler: ErrorHandler):
        self.component_name = component_name
        self.error_handler = error_handler
        self.start_time = None
        self.success_count = 0
        self.error_count = 0
        self.total_time = 0.0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.total_time += duration
            
            if exc_type is None:
                self.success_count += 1
            else:
                self.error_count += 1
                
                # Categorize the exception
                category = self._categorize_exception(exc_type)
                severity = self._determine_severity(exc_type)
                
                self.error_handler.log_error(
                    error=exc_val,
                    category=category,
                    severity=severity,
                    component=self.component_name,
                    system_state={'duration': duration}
                )
        
        return False  # Don't suppress exceptions
    
    def _categorize_exception(self, exc_type) -> ErrorCategory:
        if 'timeout' in str(exc_type).lower():
            return ErrorCategory.TIMEOUT_ERROR
        elif 'network' in str(exc_type).lower() or 'connection' in str(exc_type).lower():
            return ErrorCategory.NETWORK_ERROR
        elif 'parse' in str(exc_type).lower() or 'json' in str(exc_type).lower():
            return ErrorCategory.PARSING_ERROR
        elif 'api' in str(exc_type).lower() or 'http' in str(exc_type).lower():
            return ErrorCategory.API_ERROR
        else:
            return ErrorCategory.VALIDATION_ERROR
    
    def _determine_severity(self, exc_type) -> ErrorSeverity:
        critical_errors = ['SystemExit', 'KeyboardInterrupt', 'MemoryError']
        high_errors = ['ConnectionError', 'TimeoutError', 'HTTPError']
        
        exc_name = exc_type.__name__
        
        if exc_name in critical_errors:
            return ErrorSeverity.CRITICAL
        elif exc_name in high_errors:
            return ErrorSeverity.HIGH
        elif 'Error' in exc_name:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def get_stats(self) -> Dict[str, Any]:
        total_requests = self.success_count + self.error_count
        
        if total_requests == 0:
            return {
                'component': self.component_name,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'total_requests': 0,
                'error_count': 0
            }
        
        return {
            'component': self.component_name,
            'success_rate': self.success_count / total_requests,
            'avg_response_time': self.total_time / total_requests,
            'total_requests': total_requests,
            'error_count': self.error_count
        }


# Global error handler instance
error_handler = ErrorHandler()
