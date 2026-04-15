package repository

import (
	"context"
	"testing"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	cismodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/model"
	mastermodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/model"
)

func TestListLegacyStatesRequiresLegacyDB(t *testing.T) {
	repo := New(nil, nil)
	_, err := repo.ListLegacyStates(context.Background(), nil)
	if err == nil {
		t.Fatal("expected error when legacy db is not configured")
	}
}

func TestListLegacyCaseTypesAndActs(t *testing.T) {
	db, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open sqlite: %v", err)
	}
	if err := db.AutoMigrate(&cismodel.LegacyState{}, &cismodel.LegacyCaseType{}, &cismodel.LegacyAct{}); err != nil {
		t.Fatalf("failed to migrate sqlite tables: %v", err)
	}

	stateName := "Sikkim"
	caseTypeName := "Writ"
	actName := "Constitution of India"
	if err := db.Create(&cismodel.LegacyState{StateID: 1, State: &stateName}).Error; err != nil {
		t.Fatalf("failed to seed legacy state: %v", err)
	}
	if err := db.Create(&cismodel.LegacyCaseType{CaseType: 1, TypeName: &caseTypeName}).Error; err != nil {
		t.Fatalf("failed to seed legacy case type: %v", err)
	}
	if err := db.Create(&cismodel.LegacyAct{ActCode: 101, ActName: &actName}).Error; err != nil {
		t.Fatalf("failed to seed legacy act: %v", err)
	}

	repo := New(nil, db)
	states, err := repo.ListLegacyStates(context.Background(), nil)
	if err != nil || len(states) != 1 {
		t.Fatalf("expected one state, got err=%v len=%d", err, len(states))
	}
	caseTypes, err := repo.ListLegacyCaseTypes(context.Background())
	if err != nil || len(caseTypes) != 1 {
		t.Fatalf("expected one case type, got err=%v len=%d", err, len(caseTypes))
	}
	acts, err := repo.ListLegacyActs(context.Background())
	if err != nil || len(acts) != 1 {
		t.Fatalf("expected one act, got err=%v len=%d", err, len(acts))
	}
}

func TestUpsertCaseTypeCreatesAndUpdates(t *testing.T) {
	primary, err := gorm.Open(sqlite.Open("file:testct_primary?mode=memory&cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open primary sqlite: %v", err)
	}
	if err := primary.AutoMigrate(&mastermodel.CaseType{}); err != nil {
		t.Fatalf("failed to migrate primary: %v", err)
	}

	legacy, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open legacy sqlite: %v", err)
	}
	if err := legacy.AutoMigrate(&cismodel.LegacyCaseType{}); err != nil {
		t.Fatalf("failed to migrate legacy: %v", err)
	}

	typeName := "Criminal"
	estCodeSrc := "CRM001"
	repo := New(primary, legacy)

	created, err := repo.UpsertCaseType(context.Background(), cismodel.LegacyCaseType{
		CaseType:   10,
		TypeName:   &typeName,
		EstCodeSrc: &estCodeSrc,
	})
	if err != nil || !created {
		t.Fatalf("expected create to return true and no error, got created=%v err=%v", created, err)
	}

	var ct mastermodel.CaseType
	if err := primary.First(&ct, 10).Error; err != nil {
		t.Fatalf("failed to fetch created case type: %v", err)
	}
	if ct.TypeName == nil || *ct.TypeName != typeName {
		t.Fatalf("expected type name %q, got %+v", typeName, ct.TypeName)
	}

	newTypeName := "Updated Criminal"
	created, err = repo.UpsertCaseType(context.Background(), cismodel.LegacyCaseType{
		CaseType:   10,
		TypeName:   &newTypeName,
		EstCodeSrc: &estCodeSrc,
	})
	if err != nil || created {
		t.Fatalf("expected create to return false and no error, got created=%v err=%v", created, err)
	}

	if err := primary.First(&ct, 10).Error; err != nil {
		t.Fatalf("failed to fetch updated case type: %v", err)
	}
	if ct.TypeName == nil || *ct.TypeName != newTypeName {
		t.Fatalf("expected updated type name %q, got %q", newTypeName, *ct.TypeName)
	}
}

func TestUpsertActCreatesAndUpdates(t *testing.T) {
	primary, err := gorm.Open(sqlite.Open("file:testact_primary?mode=memory&cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open primary sqlite: %v", err)
	}
	if err := primary.AutoMigrate(&mastermodel.Act{}); err != nil {
		t.Fatalf("failed to migrate primary: %v", err)
	}

	legacy, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open legacy sqlite: %v", err)
	}
	if err := legacy.AutoMigrate(&cismodel.LegacyAct{}); err != nil {
		t.Fatalf("failed to migrate legacy: %v", err)
	}

	actName := "Indian Penal Code"
	estCodeSrc := "IPC001"
	repo := New(primary, legacy)

	created, err := repo.UpsertAct(context.Background(), cismodel.LegacyAct{
		ActCode:    494,
		ActName:    &actName,
		EstCodeSrc: &estCodeSrc,
	})
	if err != nil || !created {
		t.Fatalf("expected create to return true and no error, got created=%v err=%v", created, err)
	}

	var act mastermodel.Act
	if err := primary.First(&act, 494).Error; err != nil {
		t.Fatalf("failed to fetch created act: %v", err)
	}
	if act.ActName == nil || *act.ActName != actName {
		t.Fatalf("expected act name %q, got %+v", actName, act.ActName)
	}

	newActName := "Updated Indian Penal Code"
	created, err = repo.UpsertAct(context.Background(), cismodel.LegacyAct{
		ActCode:    494,
		ActName:    &newActName,
		EstCodeSrc: &estCodeSrc,
	})
	if err != nil || created {
		t.Fatalf("expected create to return false and no error, got created=%v err=%v", created, err)
	}

	if err := primary.First(&act, 494).Error; err != nil {
		t.Fatalf("failed to fetch updated act: %v", err)
	}
	if act.ActName == nil || *act.ActName != newActName {
		t.Fatalf("expected updated act name %q, got %q", newActName, *act.ActName)
	}
}
