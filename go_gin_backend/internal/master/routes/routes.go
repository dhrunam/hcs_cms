package routes

import (
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	coremiddleware "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/middleware"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/handler"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/repository"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/service"
)

func Register(router *gin.RouterGroup, db *gorm.DB, jwtSecret string) {
	repo := repository.New(db)
	svc := service.New(repo)
	h := handler.New(svc)

	// Operational endpoints require authentication
	master := router.Group("/master")
	master.Use(coremiddleware.AuthRequired(jwtSecret))
	master.GET("/districts", h.ListDistricts)
	master.GET("/courts", h.ListCourts)
	master.GET("/org-types", h.ListOrgTypes)

	// Read-only master data: optional auth (backward compatible)
	readOnly := router.Group("/master")
	readOnly.Use(coremiddleware.OptionalAuth(jwtSecret))
	readOnly.GET("/case-types", h.ListCaseTypes)
	readOnly.GET("/states", h.ListStates)
	readOnly.GET("/acts", h.ListActs)
	readOnly.GET("/org-names", h.ListOrgNames)
}
