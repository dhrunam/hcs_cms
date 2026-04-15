package logging

import "log"

func Info(format string, args ...interface{}) {
	log.Printf(format, args...)
}
