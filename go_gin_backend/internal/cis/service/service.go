package service

import (
	"context"

	cismodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/model"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/repository"
)

type MigrationSummary struct {
	Created int `json:"created"`
	Updated int `json:"updated"`
	Skipped int `json:"skipped"`
}

type Service struct {
	repository *repository.Repository
}

func New(repo *repository.Repository) *Service {
	return &Service{repository: repo}
}

func (s *Service) ListLegacyStates(ctx context.Context) ([]cismodel.LegacyState, error) {
	return s.repository.ListLegacyStates(ctx, nil)
}

func (s *Service) ListLegacyCaseTypes(ctx context.Context) ([]cismodel.LegacyCaseType, error) {
	return s.repository.ListLegacyCaseTypes(ctx)
}

func (s *Service) ListLegacyActs(ctx context.Context) ([]cismodel.LegacyAct, error) {
	return s.repository.ListLegacyActs(ctx)
}

func (s *Service) MigrateStates(ctx context.Context, limit *int) (MigrationSummary, error) {
	items, err := s.repository.ListLegacyStates(ctx, limit)
	if err != nil {
		return MigrationSummary{}, err
	}

	summary := MigrationSummary{}
	for _, item := range items {
		if item.StateID == 0 {
			summary.Skipped++
			continue
		}

		created, upsertErr := s.repository.UpsertState(ctx, item)
		if upsertErr != nil {
			return MigrationSummary{}, upsertErr
		}
		if created {
			summary.Created++
		} else {
			summary.Updated++
		}
	}

	return summary, nil
}

func (s *Service) MigrateCaseTypes(ctx context.Context, limit *int) (MigrationSummary, error) {
	items, err := s.repository.ListLegacyCaseTypes(ctx)
	if err != nil {
		return MigrationSummary{}, err
	}

	summary := MigrationSummary{}
	for _, item := range items {
		if item.CaseType == 0 {
			summary.Skipped++
			continue
		}

		created, upsertErr := s.repository.UpsertCaseType(ctx, item)
		if upsertErr != nil {
			return MigrationSummary{}, upsertErr
		}
		if created {
			summary.Created++
		} else {
			summary.Updated++
		}
	}

	return summary, nil
}

func (s *Service) MigrateActs(ctx context.Context, limit *int) (MigrationSummary, error) {
	items, err := s.repository.ListLegacyActs(ctx)
	if err != nil {
		return MigrationSummary{}, err
	}

	summary := MigrationSummary{}
	for _, item := range items {
		if item.ActCode == 0 {
			summary.Skipped++
			continue
		}

		created, upsertErr := s.repository.UpsertAct(ctx, item)
		if upsertErr != nil {
			return MigrationSummary{}, upsertErr
		}
		if created {
			summary.Created++
		} else {
			summary.Updated++
		}
	}

	return summary, nil
}
