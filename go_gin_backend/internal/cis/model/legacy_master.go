package model

import "time"

type LegacyState struct {
	StateID      uint       `json:"state_id" gorm:"column:state_id;primaryKey"`
	State        *string    `json:"state" gorm:"column:state"`
	CreateModify *time.Time `json:"create_modify" gorm:"column:create_modify"`
	EstCodeSrc   *string    `json:"est_code_src" gorm:"column:est_code_src"`
	NationalCode *string    `json:"national_code" gorm:"column:national_code"`
}

func (LegacyState) TableName() string {
	return "state"
}

type LegacyCaseType struct {
	CaseType   int16   `json:"case_type" gorm:"column:case_type;primaryKey"`
	TypeName   *string `json:"type_name" gorm:"column:type_name"`
	LTypeName  *string `json:"ltype_name" gorm:"column:ltype_name"`
	FullForm   *string `json:"full_form" gorm:"column:full_form"`
	LFullForm  *string `json:"lfull_form" gorm:"column:lfull_form"`
	TypeFlag   *string `json:"type_flag" gorm:"column:type_flag"`
	EstCodeSrc *string `json:"est_code_src" gorm:"column:est_code_src"`
	RegNo      *int    `json:"reg_no" gorm:"column:reg_no"`
	RegYear    *int16  `json:"reg_year" gorm:"column:reg_year"`
}

func (LegacyCaseType) TableName() string {
	return "case_type_t"
}

type LegacyAct struct {
	ActCode      int64      `json:"actcode" gorm:"column:actcode;primaryKey"`
	ActName      *string    `json:"actname" gorm:"column:actname"`
	LActName     *string    `json:"lactname" gorm:"column:lactname"`
	ActType      *string    `json:"acttype" gorm:"column:acttype"`
	Display      *string    `json:"display" gorm:"column:display"`
	NationalCode *string    `json:"national_code" gorm:"column:national_code"`
	ShortAct     *string    `json:"shortact" gorm:"column:shortact"`
	AMD          *string    `json:"amd" gorm:"column:amd"`
	CreateModify *time.Time `json:"create_modify" gorm:"column:create_modify"`
	EstCodeSrc   *string    `json:"est_code_src" gorm:"column:est_code_src"`
}

func (LegacyAct) TableName() string {
	return "act_t"
}
