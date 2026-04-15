package repository

import (
	"context"
	"strings"

	"gorm.io/gorm"

	cismodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/model"
	coreerrors "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/errors"
	mastermodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/model"
)

type Repository struct {
	primary *gorm.DB
	legacy  *gorm.DB
}

func New(primary, legacy *gorm.DB) *Repository {
	return &Repository{primary: primary, legacy: legacy}
}

func (r *Repository) ListLegacyStates(ctx context.Context, limit *int) ([]cismodel.LegacyState, error) {
	if err := r.ensureLegacyDB(); err != nil {
		return nil, err
	}
	var items []cismodel.LegacyState
	query := r.legacy.WithContext(ctx).Order("state asc")
	if limit != nil && *limit > 0 {
		query = query.Limit(*limit)
	}
	if err := query.Find(&items).Error; err != nil {
		return nil, err
	}
	return items, nil
}

func (r *Repository) ListLegacyCaseTypes(ctx context.Context) ([]cismodel.LegacyCaseType, error) {
	if err := r.ensureLegacyDB(); err != nil {
		return nil, err
	}
	var items []cismodel.LegacyCaseType
	if err := r.legacy.WithContext(ctx).Order("type_name asc").Find(&items).Error; err != nil {
		return nil, err
	}
	return items, nil
}

func (r *Repository) ListLegacyActs(ctx context.Context) ([]cismodel.LegacyAct, error) {
	if err := r.ensureLegacyDB(); err != nil {
		return nil, err
	}
	var items []cismodel.LegacyAct
	if err := r.legacy.WithContext(ctx).Order("actname asc").Find(&items).Error; err != nil {
		return nil, err
	}
	return items, nil
}

func (r *Repository) UpsertState(ctx context.Context, item cismodel.LegacyState) (bool, error) {
	if err := r.ensurePrimaryDB(); err != nil {
		return false, err
	}

	var existing mastermodel.State
	err := r.primary.WithContext(ctx).First(&existing, item.StateID).Error
	if err != nil && err != gorm.ErrRecordNotFound {
		return false, err
	}

	target := mastermodel.State{
		AuditFields: mastermodel.AuditFields{
			ID:       item.StateID,
			IsActive: true,
		},
		State:        item.State,
		CreateModify: item.CreateModify,
		EstCodeSrc:   truncateOrEmpty(item.EstCodeSrc, 6),
		NationalCode: truncateOrNil(item.NationalCode, 15),
	}

	if err == gorm.ErrRecordNotFound {
		if createErr := r.primary.WithContext(ctx).Create(&target).Error; createErr != nil {
			return false, createErr
		}
		return true, nil
	}

	updates := map[string]interface{}{
		"state":         target.State,
		"create_modify": target.CreateModify,
		"est_code_src":  target.EstCodeSrc,
		"national_code": target.NationalCode,
		"is_active":     target.IsActive,
	}
	if updateErr := r.primary.WithContext(ctx).Model(&mastermodel.State{}).Where("id = ?", item.StateID).Updates(updates).Error; updateErr != nil {
		return false, updateErr
	}
	return false, nil
}

func (r *Repository) UpsertCaseType(ctx context.Context, item cismodel.LegacyCaseType) (bool, error) {
	if err := r.ensurePrimaryDB(); err != nil {
		return false, err
	}

	var existing mastermodel.CaseType
	err := r.primary.WithContext(ctx).First(&existing, item.CaseType).Error
	if err != nil && err != gorm.ErrRecordNotFound {
		return false, err
	}

	target := mastermodel.CaseType{
		AuditFields: mastermodel.AuditFields{
			ID:       uint(item.CaseType),
			IsActive: true,
		},
		CaseType:   item.CaseType,
		TypeName:   item.TypeName,
		LTypeName:  item.LTypeName,
		FullForm:   item.FullForm,
		LFullForm:  item.LFullForm,
		TypeFlag:   truncateOrEmpty(item.TypeFlag, 1),
		EstCodeSrc: truncateOrEmpty(item.EstCodeSrc, 6),
		RegNo:      derefIntDefault(item.RegNo, 0),
		RegYear:    derefInt16Default(item.RegYear, 0),
	}

	if err == gorm.ErrRecordNotFound {
		if createErr := r.primary.WithContext(ctx).Create(&target).Error; createErr != nil {
			return false, createErr
		}
		return true, nil
	}

	updates := map[string]interface{}{
		"type_name":    target.TypeName,
		"ltype_name":   target.LTypeName,
		"full_form":    target.FullForm,
		"lfull_form":   target.LFullForm,
		"type_flag":    target.TypeFlag,
		"est_code_src": target.EstCodeSrc,
		"reg_no":       target.RegNo,
		"reg_year":     target.RegYear,
		"is_active":    target.IsActive,
	}
	if updateErr := r.primary.WithContext(ctx).Model(&mastermodel.CaseType{}).Where("id = ?", target.ID).Updates(updates).Error; updateErr != nil {
		return false, updateErr
	}
	return false, nil
}

func (r *Repository) UpsertAct(ctx context.Context, item cismodel.LegacyAct) (bool, error) {
	if err := r.ensurePrimaryDB(); err != nil {
		return false, err
	}

	var existing mastermodel.Act
	err := r.primary.WithContext(ctx).First(&existing, item.ActCode).Error
	if err != nil && err != gorm.ErrRecordNotFound {
		return false, err
	}

	target := mastermodel.Act{
		ActCode:      item.ActCode,
		ActName:      item.ActName,
		LActName:     item.LActName,
		ActType:      truncateOrEmpty(item.ActType, 10),
		Display:      truncateOrEmpty(item.Display, 1),
		NationalCode: truncateOrNil(item.NationalCode, 15),
		ShortAct:     item.ShortAct,
		AMD:          item.AMD,
		CreateModify: item.CreateModify,
		EstCodeSrc:   truncateOrEmpty(item.EstCodeSrc, 6),
		AuditFields: mastermodel.AuditFields{
			ID:       uint(item.ActCode),
			IsActive: true,
		},
	}

	if err == gorm.ErrRecordNotFound {
		if createErr := r.primary.WithContext(ctx).Create(&target).Error; createErr != nil {
			return false, createErr
		}
		return true, nil
	}

	updates := map[string]interface{}{
		"actname":       target.ActName,
		"lactname":      target.LActName,
		"acttype":       target.ActType,
		"display":       target.Display,
		"national_code": target.NationalCode,
		"shortact":      target.ShortAct,
		"amd":           target.AMD,
		"create_modify": target.CreateModify,
		"est_code_src":  target.EstCodeSrc,
		"is_active":     target.IsActive,
	}
	if updateErr := r.primary.WithContext(ctx).Model(&mastermodel.Act{}).Where("actcode = ?", item.ActCode).Updates(updates).Error; updateErr != nil {
		return false, updateErr
	}
	return false, nil
}

func (r *Repository) ensureLegacyDB() error {
	if r.legacy == nil {
		return coreerrors.HTTPError{Status: 503, Message: "legacy cis database is not configured"}
	}
	return nil
}

func (r *Repository) ensurePrimaryDB() error {
	if r.primary == nil {
		return coreerrors.HTTPError{Status: 503, Message: "primary database is not configured"}
	}
	return nil
}

func truncateOrEmpty(value *string, maxLen int) string {
	if value == nil {
		return ""
	}
	trimmed := strings.TrimSpace(*value)
	if trimmed == "" {
		return ""
	}
	if len(trimmed) > maxLen {
		return trimmed[:maxLen]
	}
	return trimmed
}

func truncateOrNil(value *string, maxLen int) *string {
	if value == nil {
		return nil
	}
	trimmed := strings.TrimSpace(*value)
	if trimmed == "" {
		return nil
	}
	if len(trimmed) > maxLen {
		trimmed = trimmed[:maxLen]
	}
	return &trimmed
}

func derefIntDefault(value *int, defaultVal int) int {
	if value == nil {
		return defaultVal
	}
	return *value
}

func derefInt16Default(value *int16, defaultVal int16) int16 {
	if value == nil {
		return defaultVal
	}
	return *value
}
