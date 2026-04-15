package db

import "gorm.io/gorm"

func IsLegacyEnabled(db *gorm.DB) bool {
	return db != nil
}
