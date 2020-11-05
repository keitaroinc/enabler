package util

import (
	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
)

func InSlice(slice []string, val string) (int, bool) {
	for i, item := range slice {
		if item == val {
			return i, true
		}
	}
	return -1, false
}

func NewLogger(level string, formatter logrus.Formatter) *logrus.Logger {
	// initialize new logger
	log := logrus.New()
	log.Formatter = &logrus.TextFormatter{FullTimestamp: true}

	if formatter != nil {
		log.Formatter = formatter
	}
	// set level
	lvl, err := logrus.ParseLevel(level)
	if err != nil {
		log.Error(errors.Wrapf(err, "Unable to parse log level (level=%s), setting default", level))
		log.SetLevel(logrus.InfoLevel)
	} else {
		log.Debugf("Setting log level (level=%s)", lvl)
		log.SetLevel(lvl)
	}
	return log
}
