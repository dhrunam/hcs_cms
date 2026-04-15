package db

import (
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/config"
)

type Provider struct {
	Primary *gorm.DB
	Legacy  *gorm.DB
}

func NewProvider(cfg config.Config) (*Provider, error) {
	provider := &Provider{}

	if cfg.DatabaseURL != "" {
		primary, err := gorm.Open(postgres.Open(cfg.DatabaseURL), &gorm.Config{})
		if err != nil {
			return nil, err
		}
		provider.Primary = primary
	}

	if cfg.LegacyDatabaseURL != "" {
		legacy, err := gorm.Open(postgres.Open(cfg.LegacyDatabaseURL), &gorm.Config{})
		if err != nil {
			return nil, err
		}
		provider.Legacy = legacy
	}

	return provider, nil
}
