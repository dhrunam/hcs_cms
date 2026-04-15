package service

import (
	"context"
	"testing"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	cismodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/model"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/repository"
	mastermodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/model"
)

func TestMigrateStatesCreatesAndUpdates(t *testing.T) {
	primary, err := gorm.Open(sqlite.Open("file:primary_state_migration?mode=memory&cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open primary sqlite: %v", err)
	}
	legacy, err := gorm.Open(sqlite.Open("file:legacy_state_migration?mode=memory&cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open legacy sqlite: %v", err)
	}

	if err := primary.AutoMigrate(&mastermodel.State{}); err != nil {
		t.Fatalf("failed to migrate primary state model: %v", err)
	}
	if err := legacy.AutoMigrate(&cismodel.LegacyState{}); err != nil {
		t.Fatalf("failed to migrate legacy state model: %v", err)
	}

	legacyState1 := "Updated Sikkim"
	legacyState2 := "West Bengal"
	estCode := "SKNM01234"
	nationalCode := "12345678901234567890"
	if err := legacy.Create(&cismodel.LegacyState{StateID: 1, State: &legacyState1, EstCodeSrc: &estCode, NationalCode: &nationalCode}).Error; err != nil {
		t.Fatalf("failed to seed legacy state 1: %v", err)
	}
	if err := legacy.Create(&cismodel.LegacyState{StateID: 2, State: &legacyState2}).Error; err != nil {
		t.Fatalf("failed to seed legacy state 2: %v", err)
	}

	existingName := "Old Sikkim"
	if err := primary.Create(&mastermodel.State{
		AuditFields: mastermodel.AuditFields{ID: 1, IsActive: true},
		State:       &existingName,
		EstCodeSrc:  "OLD",
	}).Error; err != nil {
		t.Fatalf("failed to seed existing primary state: %v", err)
	}

	svc := New(repository.New(primary, legacy))
	summary, err := svc.MigrateStates(context.Background(), nil)
	if err != nil {
		t.Fatalf("migrate states failed: %v", err)
	}

	if summary.Created != 1 || summary.Updated != 1 || summary.Skipped != 0 {
		t.Fatalf("unexpected summary: %+v", summary)
	}

	var state1 mastermodel.State
	if err := primary.First(&state1, 1).Error; err != nil {
		t.Fatalf("failed to fetch migrated state 1: %v", err)
	}
	if state1.State == nil || *state1.State != legacyState1 {
		t.Fatalf("expected updated state name %q, got %+v", legacyState1, state1.State)
	}
	if state1.EstCodeSrc != "SKNM01" {
		t.Fatalf("expected truncated est_code_src SKNM01, got %q", state1.EstCodeSrc)
	}
	if state1.NationalCode == nil || *state1.NationalCode != "123456789012345" {
		t.Fatalf("expected truncated national_code, got %+v", state1.NationalCode)
	}

	var state2 mastermodel.State
	if err := primary.First(&state2, 2).Error; err != nil {
		t.Fatalf("failed to fetch created state 2: %v", err)
	}
	if state2.State == nil || *state2.State != legacyState2 {
		t.Fatalf("expected created state name %q, got %+v", legacyState2, state2.State)
	}
}

func TestMigrateStatesRequiresBothDatabases(t *testing.T) {
	svc := New(repository.New(nil, nil))
	_, err := svc.MigrateStates(context.Background(), nil)
	if err == nil {
		t.Fatal("expected migration to fail when databases are not configured")
	}
}

func TestMigrateCaseTypesCreatesAndUpdates(t *testing.T) {
	primary, err := gorm.Open(sqlite.Open("file:primary_ct_migration?mode=memory&cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open primary sqlite: %v", err)
	}
	legacy, err := gorm.Open(sqlite.Open("file:legacy_ct_migration?mode=memory&cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open legacy sqlite: %v", err)
	}

	if err := primary.AutoMigrate(&mastermodel.CaseType{}); err != nil {
		t.Fatalf("failed to migrate primary case_type model: %v", err)
	}
	if err := legacy.AutoMigrate(&cismodel.LegacyCaseType{}); err != nil {
		t.Fatalf("failed to migrate legacy case_type model: %v", err)
	}

	typeName := "Civil"
	lTypeName := "नागरिक"
	fullForm := "Civil Suit"
	typeFlag := "Y"
	estCodeSrc := "CVL001"
	regNo := 100
	regYear := int16(2020)
	if err := legacy.Create(&cismodel.LegacyCaseType{
		CaseType:   1,
		TypeName:   &typeName,
		LTypeName:  &lTypeName,
		FullForm:   &fullForm,
		TypeFlag:   &typeFlag,
		EstCodeSrc: &estCodeSrc,
		RegNo:      &regNo,
		RegYear:    &regYear,
	}).Error; err != nil {
		t.Fatalf("failed to seed legacy case type 1: %v", err)
	}

	existingName := "Old Criminal"
	if err := primary.Create(&mastermodel.CaseType{
		AuditFields: mastermodel.AuditFields{ID: 2, IsActive: true},
		CaseType:    2,
		TypeName:    &existingName,
		TypeFlag:    "C",
		EstCodeSrc:  "OLD",
	}).Error; err != nil {
		t.Fatalf("failed to seed existing primary case type: %v", err)
	}

	svc := New(repository.New(primary, legacy))
	summary, err := svc.MigrateCaseTypes(context.Background(), nil)
	if err != nil {
		t.Fatalf("migrate case types failed: %v", err)
	}

	if summary.Created != 1 || summary.Updated != 0 || summary.Skipped != 0 {
		t.Fatalf("unexpected summary for case types: %+v", summary)
	}

	var ct1 mastermodel.CaseType
	if err := primary.First(&ct1, 1).Error; err != nil {
		t.Fatalf("failed to fetch migrated case type 1: %v", err)
	}
	if ct1.TypeName == nil || *ct1.TypeName != typeName {
		t.Fatalf("expected type name %q, got %+v", typeName, ct1.TypeName)
	}
}

func TestMigrateActsCreatesAndUpdates(t *testing.T) {
	primary, err := gorm.Open(sqlite.Open("file:primary_act_migration?mode=memory&cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open primary sqlite: %v", err)
	}
	legacy, err := gorm.Open(sqlite.Open("file:legacy_act_migration?mode=memory&cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open legacy sqlite: %v", err)
	}

	if err := primary.AutoMigrate(&mastermodel.Act{}); err != nil {
		t.Fatalf("failed to migrate primary act model: %v", err)
	}
	if err := legacy.AutoMigrate(&cismodel.LegacyAct{}); err != nil {
		t.Fatalf("failed to migrate legacy act model: %v", err)
	}

	actName := "Indian Penal Code"
	lActName := "भारतीय दंड संहिता"
	actType := "Criminal"
	display := "Y"
	estCodeSrc := "IPC001"
	nationalCode := "12345678901234567890"
	if err := legacy.Create(&cismodel.LegacyAct{
		ActCode:      494,
		ActName:      &actName,
		LActName:     &lActName,
		ActType:      &actType,
		Display:      &display,
		EstCodeSrc:   &estCodeSrc,
		NationalCode: &nationalCode,
	}).Error; err != nil {
		t.Fatalf("failed to seed legacy act: %v", err)
	}

	existingName := "Old Act"
	if err := primary.Create(&mastermodel.Act{
		ActCode:     495,
		ActName:     &existingName,
		ActType:     "Civil",
		Display:     "N",
		EstCodeSrc:  "OLD",
		AuditFields: mastermodel.AuditFields{ID: 495, IsActive: true},
	}).Error; err != nil {
		t.Fatalf("failed to seed existing primary act: %v", err)
	}

	svc := New(repository.New(primary, legacy))
	summary, err := svc.MigrateActs(context.Background(), nil)
	if err != nil {
		t.Fatalf("migrate acts failed: %v", err)
	}

	if summary.Created != 1 || summary.Updated != 0 || summary.Skipped != 0 {
		t.Fatalf("unexpected summary for acts: %+v", summary)
	}

	var act1 mastermodel.Act
	if err := primary.First(&act1, 494).Error; err != nil {
		t.Fatalf("failed to fetch migrated act: %v", err)
	}
	if act1.ActName == nil || *act1.ActName != actName {
		t.Fatalf("expected act name %q, got %+v", actName, act1.ActName)
	}
	if act1.NationalCode == nil || *act1.NationalCode != "123456789012345" {
		t.Fatalf("expected truncated national_code, got %+v", act1.NationalCode)
	}
}
