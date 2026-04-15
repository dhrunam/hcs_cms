package routes

import (
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	coremiddleware "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/middleware"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/handler"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/repository"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/service"
)

// Register wires the CIS migration endpoints as admin-only operations.
// The public-facing CIS read API remains unimplemented to match Django behavior.
func Register(router *gin.RouterGroup, primaryDB, legacyDB *gorm.DB, jwtSecret string) {
	repo := repository.New(primaryDB, legacyDB)
	svc := service.New(repo)
	h := handler.New(svc)

	// Admin-only migration endpoints
	migrate := router.Group("/cis/migrate")
	migrate.Use(coremiddleware.AuthRequired(jwtSecret))
	migrate.POST("/states", h.MigrateStates)
	migrate.POST("/case-types", h.MigrateCaseTypes)
	migrate.POST("/acts", h.MigrateActs)
	migrate.POST("/all", h.MigrateAll)
}
