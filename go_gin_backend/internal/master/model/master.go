package model

import "time"

type AuditFields struct {
	ID        uint       `json:"id" gorm:"column:id;primaryKey"`
	CreatedAt *time.Time `json:"created_at" gorm:"column:created_at"`
	UpdatedAt *time.Time `json:"updated_at" gorm:"column:updated_at"`
	CreatedBy *uint      `json:"created_by" gorm:"column:created_by_id"`
	UpdatedBy *uint      `json:"updated_by" gorm:"column:updated_by_id"`
	IsActive  bool       `json:"is_active" gorm:"column:is_active"`
}

type CaseType struct {
	AuditFields
	CaseType   int16   `json:"case_type" gorm:"column:case_type"`
	TypeName   *string `json:"type_name" gorm:"column:type_name"`
	LTypeName  *string `json:"ltype_name" gorm:"column:ltype_name"`
	FullForm   *string `json:"full_form" gorm:"column:full_form"`
	LFullForm  *string `json:"lfull_form" gorm:"column:lfull_form"`
	TypeFlag   string  `json:"type_flag" gorm:"column:type_flag"`
	EstCodeSrc string  `json:"est_code_src" gorm:"column:est_code_src"`
	RegNo      int     `json:"reg_no" gorm:"column:reg_no"`
	RegYear    int16   `json:"reg_year" gorm:"column:reg_year"`
}

func (CaseType) TableName() string {
	return "case_type_t"
}

type State struct {
	AuditFields
	State        *string    `json:"state" gorm:"column:state"`
	CreateModify *time.Time `json:"create_modify" gorm:"column:create_modify"`
	EstCodeSrc   string     `json:"est_code_src" gorm:"column:est_code_src"`
	NationalCode *string    `json:"national_code" gorm:"column:national_code"`
}

func (State) TableName() string {
	return "state"
}

type District struct {
	AuditFields
	StateID     *uint   `json:"state_id" gorm:"column:state_id_id"`
	District    *string `json:"district" gorm:"column:district"`
	NatinalCode *string `json:"natinal_code" gorm:"column:natinal_code"`
}

func (District) TableName() string {
	return "district"
}

type Court struct {
	AuditFields
	CourtName  *string `json:"court_name" gorm:"column:court_name"`
	Address    *string `json:"address" gorm:"column:address"`
	EstCodeSrc string  `json:"est_code_src" gorm:"column:est_code_src"`
}

func (Court) TableName() string {
	return "court"
}

type OrgType struct {
	AuditFields
	OrgType      *string `json:"orgtype" gorm:"column:orgtype"`
	NationalCode *string `json:"national_code" gorm:"column:national_code"`
}

func (OrgType) TableName() string {
	return "orgtype_t"
}

type OrgName struct {
	AuditFields
	OrgTypeID     *uint   `json:"orgtype" gorm:"column:orgtype_id"`
	OrgName       *string `json:"orgname" gorm:"column:orgname"`
	ContactPerson *string `json:"contactperson" gorm:"column:contactperson"`
	Address       *string `json:"address" gorm:"column:address"`
	StateID       *uint   `json:"state_id" gorm:"column:state_id_id"`
	DistrictID    *uint   `json:"district_id" gorm:"column:district_id_id"`
	TalukaCode    int16   `json:"taluka_code" gorm:"column:taluka_code"`
	VillageCode   int     `json:"village_code" gorm:"column:village_code"`
	Email         *string `json:"email" gorm:"column:email"`
	Mobile        *string `json:"mobile" gorm:"column:mobile"`
	Phone         *string `json:"phone" gorm:"column:phone"`
	Fax           *string `json:"fax" gorm:"column:fax"`
	Village1Code  int     `json:"village1_code" gorm:"column:village1_code"`
	Village2Code  int     `json:"village2_code" gorm:"column:village2_code"`
	TownCode      int     `json:"town_code" gorm:"column:town_code"`
	WardCode      int     `json:"ward_code" gorm:"column:ward_code"`
	NationalCode  *string `json:"national_code" gorm:"column:national_code"`
	EstCodeSrc    string  `json:"est_code_src" gorm:"column:est_code_src"`
}

func (OrgName) TableName() string {
	return "orgname_t"
}

type Act struct {
	ActCode      int64      `json:"actcode" gorm:"column:actcode;primaryKey"`
	ActName      *string    `json:"actname" gorm:"column:actname"`
	LActName     *string    `json:"lactname" gorm:"column:lactname"`
	ActType      string     `json:"acttype" gorm:"column:acttype"`
	Display      string     `json:"display" gorm:"column:display"`
	NationalCode *string    `json:"national_code" gorm:"column:national_code"`
	ShortAct     *string    `json:"shortact" gorm:"column:shortact"`
	AMD          *string    `json:"amd" gorm:"column:amd"`
	CreateModify *time.Time `json:"create_modify" gorm:"column:create_modify"`
	EstCodeSrc   string     `json:"est_code_src" gorm:"column:est_code_src"`
	AuditFields
}

func (Act) TableName() string {
	return "act_t"
}
