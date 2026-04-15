package repository

import (
	"context"

	"gorm.io/gorm"

	accountmodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/accounts/model"
	coreerrors "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/errors"
)

type Repository struct {
	db *gorm.DB
}

func New(db *gorm.DB) *Repository {
	return &Repository{db: db}
}

func (r *Repository) GetUserByID(ctx context.Context, id uint) (accountmodel.User, error) {
	if err := r.ensureDB(); err != nil {
		return accountmodel.User{}, err
	}

	var user accountmodel.User
	if err := r.db.WithContext(ctx).First(&user, id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return accountmodel.User{}, coreerrors.HTTPError{Status: 404, Message: "user not found"}
		}
		return accountmodel.User{}, err
	}
	return user, nil
}

func (r *Repository) GetUserGroups(ctx context.Context, userID uint) ([]string, error) {
	if err := r.ensureDB(); err != nil {
		return nil, err
	}

	var groups []string
	err := r.db.WithContext(ctx).
		Table("auth_group as g").
		Select("g.name").
		Joins("join auth_user_groups ug on ug.group_id = g.id").
		Where("ug.user_id = ?", userID).
		Order("g.name asc").
		Scan(&groups).Error
	if err != nil {
		return nil, err
	}

	return groups, nil
}

func (r *Repository) GetRegistrationProfile(ctx context.Context, userID uint) (*accountmodel.RegistrationProfile, error) {
	if err := r.ensureDB(); err != nil {
		return nil, err
	}

	var profile accountmodel.RegistrationProfile
	err := r.db.WithContext(ctx).Where("user_id = ?", userID).First(&profile).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, nil
		}
		return nil, err
	}

	return &profile, nil
}

func (r *Repository) ensureDB() error {
	if r.db == nil {
		return coreerrors.HTTPError{Status: 503, Message: "database is not configured"}
	}
	return nil
}
