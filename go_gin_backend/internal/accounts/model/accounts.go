package model

import "time"

type User struct {
	ID               uint      `json:"id" gorm:"column:id;primaryKey"`
	Username         string    `json:"username" gorm:"column:username"`
	Email            string    `json:"email" gorm:"column:email"`
	FirstName        string    `json:"first_name" gorm:"column:first_name"`
	LastName         string    `json:"last_name" gorm:"column:last_name"`
	PhoneNumber      string    `json:"phone_number" gorm:"column:phone_number"`
	Department       string    `json:"department" gorm:"column:department"`
	Designation      string    `json:"designation" gorm:"column:designation"`
	RegistrationType string    `json:"registration_type" gorm:"column:registration_type"`
	EmailVerified    bool      `json:"email_verified" gorm:"column:email_verified"`
	IsActive         bool      `json:"is_active" gorm:"column:is_active"`
	IsStaff          bool      `json:"is_staff" gorm:"column:is_staff"`
	DateJoined       time.Time `json:"date_joined" gorm:"column:date_joined"`
}

func (User) TableName() string {
	return "accounts_user"
}

type RegistrationProfile struct {
	ID                 uint      `json:"id" gorm:"column:id;primaryKey"`
	UserID             uint      `json:"user_id" gorm:"column:user_id"`
	DateOfBirth        time.Time `json:"date_of_birth" gorm:"column:date_of_birth"`
	Address            string    `json:"address" gorm:"column:address"`
	Gender             string    `json:"gender" gorm:"column:gender"`
	Photo              *string   `json:"photo" gorm:"column:photo"`
	BarID              string    `json:"bar_id" gorm:"column:bar_id"`
	BarIDFile          *string   `json:"bar_id_file" gorm:"column:bar_id_file"`
	VerificationStatus string    `json:"verification_status" gorm:"column:verification_status"`
}

func (RegistrationProfile) TableName() string {
	return "accounts_registrationprofile"
}
