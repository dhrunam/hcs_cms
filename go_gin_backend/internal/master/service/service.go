package service

import (
	"context"
	"strconv"

	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/errors"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/model"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/repository"
)

type Service struct {
	repository *repository.Repository
}

func New(repo *repository.Repository) *Service {
	return &Service{repository: repo}
}

func (s *Service) ListCaseTypes(ctx context.Context) ([]model.CaseType, error) {
	return s.repository.ListCaseTypes(ctx)
}

func (s *Service) ListStates(ctx context.Context) ([]model.State, error) {
	return s.repository.ListStates(ctx)
}

func (s *Service) ListDistricts(ctx context.Context, stateID string) ([]model.District, error) {
	if stateID == "" {
		return s.repository.ListDistricts(ctx, nil)
	}

	parsed, err := strconv.ParseUint(stateID, 10, 64)
	if err != nil {
		return nil, errors.HTTPError{Status: 400, Message: "invalid state_id"}
	}

	value := uint(parsed)
	return s.repository.ListDistricts(ctx, &value)
}

func (s *Service) ListActs(ctx context.Context) ([]model.Act, error) {
	return s.repository.ListActs(ctx)
}

func (s *Service) ListCourts(ctx context.Context) ([]model.Court, error) {
	return s.repository.ListCourts(ctx)
}

func (s *Service) ListCourtsWithPagination(ctx context.Context, page, pageSize int) ([]model.Court, int64, error) {
	return s.repository.ListCourtsWithPagination(ctx, page, pageSize)
}

func (s *Service) ListOrgTypes(ctx context.Context) ([]model.OrgType, error) {
	return s.repository.ListOrgTypes(ctx)
}

func (s *Service) ListOrgNames(ctx context.Context) ([]model.OrgName, error) {
	return s.repository.ListOrgNames(ctx)
}
