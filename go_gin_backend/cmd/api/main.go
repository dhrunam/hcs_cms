package main

import (
	"log"

	"github.com/gin-gonic/gin"

	accountsroutes "github.com/dhrunam/hcs_cms/go_gin_backend/internal/accounts/routes"
	cisroutes "github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/routes"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/config"
	coredb "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/db"
	coremiddleware "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/middleware"
	masterroutes "github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/routes"
)

func main() {
	cfg := config.Load()
	router := gin.New()

	router.Use(
		coremiddleware.RequestID(),
		coremiddleware.Logger(),
		coremiddleware.Recovery(),
		coremiddleware.CORS(),
	)

	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok", "service": cfg.AppName})
	})

	dbProvider, err := coredb.NewProvider(cfg)
	if err != nil {
		log.Fatalf("database bootstrap failed: %v", err)
	}

	apiV1 := router.Group("/api/v1")
	masterroutes.Register(apiV1, dbProvider.Primary, cfg.JWTSecret)
	cisroutes.Register(apiV1, dbProvider.Primary, dbProvider.Legacy, cfg.JWTSecret)
	accountsroutes.Register(apiV1, dbProvider.Primary, cfg.JWTSecret)

	if err := router.Run(":" + cfg.Port); err != nil {
		log.Fatalf("server failed: %v", err)
	}
}
