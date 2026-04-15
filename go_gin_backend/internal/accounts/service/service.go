package service

import (
	"context"
	"strconv"
	"strings"

	accountmodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/accounts/model"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/accounts/repository"
	coreerrors "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/errors"
)

type RegistrationProfileResponse struct {
	DateOfBirth        string  `json:"date_of_birth"`
	Address            string  `json:"address"`
	Gender             string  `json:"gender"`
	Photo              *string `json:"photo"`
	BarID              string  `json:"bar_id"`
	BarIDFile          *string `json:"bar_id_file"`
	VerificationStatus string  `json:"verification_status"`
}

type UserResponse struct {
	ID                  uint                         `json:"id"`
	Username            string                       `json:"username"`
	Email               string                       `json:"email"`
	FirstName           string                       `json:"first_name"`
	LastName            string                       `json:"last_name"`
	FullName            string                       `json:"full_name"`
	PhoneNumber         string                       `json:"phone_number"`
	Department          string                       `json:"department"`
	Designation         string                       `json:"designation"`
	RegistrationType    string                       `json:"registration_type"`
	EmailVerified       bool                         `json:"email_verified"`
	Groups              []string                     `json:"groups"`
	RegistrationProfile *RegistrationProfileResponse `json:"registration_profile"`
	IsActive            bool                         `json:"is_active"`
	IsStaff             bool                         `json:"is_staff"`
	DateJoined          string                       `json:"date_joined"`
}

type Service struct {
	repository *repository.Repository
}

func New(repo *repository.Repository) *Service {
	return &Service{repository: repo}
}

func (s *Service) Me(ctx context.Context, userID string) (UserResponse, error) {
	trimmed := strings.TrimSpace(userID)
	if trimmed == "" {
		return UserResponse{}, coreerrors.HTTPError{Status: 401, Message: "invalid token"}
	}

	parsed, err := strconv.ParseUint(trimmed, 10, 64)
	if err != nil {
		return UserResponse{}, coreerrors.HTTPError{Status: 401, Message: "invalid token"}
	}

	user, err := s.repository.GetUserByID(ctx, uint(parsed))
	if err != nil {
		return UserResponse{}, err
	}

	groups, err := s.repository.GetUserGroups(ctx, user.ID)
	if err != nil {
		return UserResponse{}, err
	}

	profile, err := s.repository.GetRegistrationProfile(ctx, user.ID)
	if err != nil {
		return UserResponse{}, err
	}

	return toUserResponse(user, groups, profile), nil
}

func toUserResponse(user accountmodel.User, groups []string, profile *accountmodel.RegistrationProfile) UserResponse {
	fullName := strings.TrimSpace(user.FirstName + " " + user.LastName)

	resp := UserResponse{
		ID:               user.ID,
		Username:         user.Username,
		Email:            user.Email,
		FirstName:        user.FirstName,
		LastName:         user.LastName,
		FullName:         fullName,
		PhoneNumber:      user.PhoneNumber,
		Department:       user.Department,
		Designation:      user.Designation,
		RegistrationType: user.RegistrationType,
		EmailVerified:    user.EmailVerified,
		Groups:           groups,
		IsActive:         user.IsActive,
		IsStaff:          user.IsStaff,
		DateJoined:       user.DateJoined.Format("2006-01-02T15:04:05Z07:00"),
	}

	if profile != nil {
		resp.RegistrationProfile = &RegistrationProfileResponse{
			DateOfBirth:        profile.DateOfBirth.Format("2006-01-02"),
			Address:            profile.Address,
			Gender:             profile.Gender,
			Photo:              profile.Photo,
			BarID:              profile.BarID,
			BarIDFile:          profile.BarIDFile,
			VerificationStatus: profile.VerificationStatus,
		}
	}

	return resp
}
