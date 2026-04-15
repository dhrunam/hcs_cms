package routes

import (
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/accounts/handler"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/accounts/repository"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/accounts/service"
	coremiddleware "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/middleware"
)

func Register(router *gin.RouterGroup, db *gorm.DB, jwtSecret string) {
	repo := repository.New(db)
	svc := service.New(repo)
	h := handler.New(svc)

	accounts := router.Group("/accounts")
	accounts.Use(func(c *gin.Context) {
		c.Set("jwt_secret", jwtSecret)
		c.Next()
	})

	auth := accounts.Group("/auth")
	auth.POST("/token/", h.NotImplemented)
	auth.POST("/token/refresh/", h.NotImplemented)
	auth.POST("/token/verify/", h.TokenVerify)
	auth.POST("/token/blacklist/", h.NotImplemented)
	auth.POST("/register/party/", h.NotImplemented)
	auth.POST("/register/advocate/", h.NotImplemented)
	auth.POST("/verify-email/", h.NotImplemented)

	users := accounts.Group("/users")
	users.Use(coremiddleware.AuthRequired(jwtSecret))
	users.GET("/me", h.Me)
	users.POST("/logout", h.Logout)
}
