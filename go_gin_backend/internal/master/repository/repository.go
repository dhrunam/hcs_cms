package repository

import (
	"context"

	"gorm.io/gorm"

	coreerrors "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/errors"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/model"
)

type Repository struct {
	db *gorm.DB
}

func New(db *gorm.DB) *Repository {
	return &Repository{db: db}
}

func (r *Repository) ListCaseTypes(ctx context.Context) ([]model.CaseType, error) {
	if err := r.ensureDB(); err != nil {
		return nil, err
	}

	var caseTypes []model.CaseType
	if err := r.db.WithContext(ctx).Order("type_name asc").Find(&caseTypes).Error; err != nil {
		return nil, err
	}
	return caseTypes, nil
}

func (r *Repository) ListStates(ctx context.Context) ([]model.State, error) {
	if err := r.ensureDB(); err != nil {
		return nil, err
	}

	var states []model.State
	if err := r.db.WithContext(ctx).Order("state asc").Find(&states).Error; err != nil {
		return nil, err
	}
	return states, nil
}

func (r *Repository) ListDistricts(ctx context.Context, stateID *uint) ([]model.District, error) {
	if err := r.ensureDB(); err != nil {
		return nil, err
	}

	query := r.db.WithContext(ctx).Model(&model.District{})
	if stateID != nil {
		query = query.Where("state_id_id = ?", *stateID)
	}

	var districts []model.District
	if err := query.Find(&districts).Error; err != nil {
		return nil, err
	}
	return districts, nil
}

func (r *Repository) ListActs(ctx context.Context) ([]model.Act, error) {
	if err := r.ensureDB(); err != nil {
		return nil, err
	}

	var acts []model.Act
	if err := r.db.WithContext(ctx).Find(&acts).Error; err != nil {
		return nil, err
	}
	return acts, nil
}

func (r *Repository) ListCourts(ctx context.Context) ([]model.Court, error) {
	if err := r.ensureDB(); err != nil {
		return nil, err
	}

	var courts []model.Court
	if err := r.db.WithContext(ctx).Find(&courts).Error; err != nil {
		return nil, err
	}
	return courts, nil
}

func (r *Repository) ListCourtsWithPagination(ctx context.Context, page, pageSize int) ([]model.Court, int64, error) {
	if err := r.ensureDB(); err != nil {
		return nil, 0, err
	}

	if page < 1 {
		page = 1
	}
	if pageSize < 1 {
		pageSize = 20
	}

	var courts []model.Court
	var total int64

	if err := r.db.WithContext(ctx).Model(&model.Court{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}

	offset := (page - 1) * pageSize
	if err := r.db.WithContext(ctx).Offset(offset).Limit(pageSize).Find(&courts).Error; err != nil {
		return nil, 0, err
	}

	return courts, total, nil
}

func (r *Repository) ListOrgTypes(ctx context.Context) ([]model.OrgType, error) {
	if err := r.ensureDB(); err != nil {
		return nil, err
	}

	var orgTypes []model.OrgType
	if err := r.db.WithContext(ctx).Find(&orgTypes).Error; err != nil {
		return nil, err
	}
	return orgTypes, nil
}

func (r *Repository) ListOrgNames(ctx context.Context) ([]model.OrgName, error) {
	if err := r.ensureDB(); err != nil {
		return nil, err
	}

	var orgNames []model.OrgName
	if err := r.db.WithContext(ctx).Order("orgname asc").Find(&orgNames).Error; err != nil {
		return nil, err
	}
	return orgNames, nil
}

func (r *Repository) ensureDB() error {
	if r.db == nil {
		return coreerrors.HTTPError{Status: 503, Message: "database is not configured"}
	}
	return nil
}
