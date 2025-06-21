type LogLevel = 'debug' | 'info' | 'warn' | 'error'

interface LogContext {
  [key: string]: unknown
}

class Logger {
  private isDevelopment = process.env.NODE_ENV === 'development'
  
  private log(level: LogLevel, message: string, context?: LogContext) {
    if (!this.isDevelopment && level === 'debug') {
      return // Skip debug logs in production
    }
    
    const timestamp = new Date().toISOString()
    const logData = {
      timestamp,
      level,
      message,
      ...context
    }
    
    // In production, you might want to send to a logging service
    if (this.isDevelopment) {
      const emoji = {
        debug: '🔍',
        info: 'ℹ️',
        warn: '⚠️',
        error: '❌'
      }[level]
      
      console[level === 'debug' ? 'log' : level](`${emoji} ${message}`, context || '')
    } else {
      // In production, only log errors to console, send others to monitoring service
      if (level === 'error') {
        console.error(logData)
      }
      // TODO: Send to monitoring service (e.g., Sentry, LogRocket)
    }
  }
  
  debug(message: string, context?: LogContext) {
    this.log('debug', message, context)
  }
  
  info(message: string, context?: LogContext) {
    this.log('info', message, context)
  }
  
  warn(message: string, context?: LogContext) {
    this.log('warn', message, context)
  }
  
  error(message: string, context?: LogContext) {
    this.log('error', message, context)
  }
  
  // Specialized loggers for different domains
  auth = {
    debug: (message: string, context?: LogContext) => this.debug(`[AUTH] ${message}`, context),
    info: (message: string, context?: LogContext) => this.info(`[AUTH] ${message}`, context),
    error: (message: string, context?: LogContext) => this.error(`[AUTH] ${message}`, context)
  }
  
  api = {
    debug: (message: string, context?: LogContext) => this.debug(`[API] ${message}`, context),
    info: (message: string, context?: LogContext) => this.info(`[API] ${message}`, context),
    error: (message: string, context?: LogContext) => this.error(`[API] ${message}`, context)
  }
  
  files = {
    debug: (message: string, context?: LogContext) => this.debug(`[FILES] ${message}`, context),
    info: (message: string, context?: LogContext) => this.info(`[FILES] ${message}`, context),
    error: (message: string, context?: LogContext) => this.error(`[FILES] ${message}`, context)
  }
}

export const logger = new Logger()

// Convenience exports
export const { debug, info, warn, error } = logger
export const { auth, api, files } = logger 